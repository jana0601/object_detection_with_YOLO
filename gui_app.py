import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np
from ultralytics import YOLO
import threading
import time

class ObjectDetectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Real-Time YOLO Object Detection")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # Initialize variables
        self.camera = None
        self.detection_active = False
        self.model = None
        self.current_frame = None
        self.latest_detections = []
        
        # Performance optimization variables
        self.frame_skip_counter = 0
        self.frame_skip_interval = 2  # Process every 3rd frame for detection
        self.confidence_threshold = 0.5  # Only show detections above 50% confidence
        self.detection_fps_counter = 0
        self.detection_fps_start_time = time.time()
        self.last_detection_time = 0
        
        # Initialize YOLO model
        self.load_model()
        
        # Create GUI
        self.create_widgets()
        
        # Camera thread
        self.camera_thread = None
        self.detection_thread = None
        
    def load_model(self):
        """Load YOLO model"""
        try:
            self.model = YOLO('yolov8n.pt')
            print("✅ YOLO model loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load YOLO model: {str(e)}")
            
    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🔍 Real-Time YOLO Object Detection", 
                              font=('Arial', 20, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Camera selection
        camera_frame = tk.Frame(control_frame, bg='#34495e')
        camera_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(camera_frame, text="Camera:", font=('Arial', 12, 'bold'), 
                fg='white', bg='#34495e').pack(side=tk.LEFT)
        
        self.camera_var = tk.StringVar(value="0")
        camera_combo = ttk.Combobox(camera_frame, textvariable=self.camera_var, 
                                   values=["0", "1", "2"], width=5)
        camera_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Performance controls
        perf_frame = tk.Frame(control_frame, bg='#34495e')
        perf_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(perf_frame, text="Confidence:", font=('Arial', 10, 'bold'), 
                fg='white', bg='#34495e').pack(side=tk.LEFT)
        
        self.confidence_var = tk.DoubleVar(value=0.5)
        confidence_scale = tk.Scale(perf_frame, from_=0.1, to=0.9, resolution=0.1,
                                  orient=tk.HORIZONTAL, variable=self.confidence_var,
                                  command=self.update_confidence_threshold,
                                  bg='#34495e', fg='white', length=100)
        confidence_scale.pack(side=tk.LEFT, padx=(5, 0))
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg='#34495e')
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.start_button = tk.Button(button_frame, text="🎥 Start Camera", 
                                     command=self.start_camera,
                                     bg='#27ae60', fg='white', 
                                     font=('Arial', 12, 'bold'),
                                     padx=20, pady=5)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(button_frame, text="⏹️ Stop Camera", 
                                    command=self.stop_camera,
                                    bg='#e74c3c', fg='white', 
                                    font=('Arial', 12, 'bold'),
                                    padx=20, pady=5, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.detect_button = tk.Button(button_frame, text="🔍 Start Detection", 
                                      command=self.toggle_detection,
                                      bg='#3498db', fg='white', 
                                      font=('Arial', 12, 'bold'),
                                      padx=20, pady=5, state=tk.DISABLED)
        self.detect_button.pack(side=tk.LEFT, padx=5)
        
        # Video frame
        video_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        video_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Video display
        self.video_label = tk.Label(video_frame, text="Click 'Start Camera' to begin", 
                                   font=('Arial', 16), fg='white', bg='#34495e')
        self.video_label.pack(expand=True)
        
        # Detection info frame
        info_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X)
        
        # Detection count
        self.detection_count_label = tk.Label(info_frame, text="Detections: 0", 
                                             font=('Arial', 12, 'bold'), 
                                             fg='white', bg='#34495e')
        self.detection_count_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Performance info
        perf_info_frame = tk.Frame(info_frame, bg='#34495e')
        perf_info_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.fps_label = tk.Label(perf_info_frame, text="Camera FPS: 0", 
                                 font=('Arial', 10, 'bold'), 
                                 fg='white', bg='#34495e')
        self.fps_label.pack(side=tk.TOP)
        
        self.detection_fps_label = tk.Label(perf_info_frame, text="Detection FPS: 0", 
                                          font=('Arial', 10, 'bold'), 
                                          fg='white', bg='#34495e')
        self.detection_fps_label.pack(side=tk.TOP)
        
        # Detection list
        self.detection_listbox = tk.Listbox(info_frame, height=4, 
                                           font=('Arial', 10), bg='#2c3e50', fg='white')
        self.detection_listbox.pack(fill=tk.X, padx=10, pady=(0, 10))
        
    def update_confidence_threshold(self, value):
        """Update confidence threshold for detection filtering"""
        self.confidence_threshold = float(value)
        print(f"Confidence threshold updated to: {self.confidence_threshold}")
        
    def start_camera(self):
        """Start camera capture"""
        try:
            camera_index = int(self.camera_var.get())
            self.camera = cv2.VideoCapture(camera_index)
            
            if not self.camera.isOpened():
                # Try alternative camera indices
                for alt_index in [0, 1, 2]:
                    if alt_index != camera_index:
                        self.camera = cv2.VideoCapture(alt_index)
                        if self.camera.isOpened():
                            print(f"✅ Camera {alt_index} opened successfully")
                            break
                else:
                    messagebox.showerror("Error", "Could not open any camera. Please check your camera connection.")
                    return
                
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Test camera by reading one frame
            ret, test_frame = self.camera.read()
            if not ret:
                messagebox.showerror("Error", "Camera is not responding properly")
                self.camera.release()
                return
            
            # Start camera thread
            self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
            self.camera_thread.start()
            
            # Update button states
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.detect_button.config(state=tk.NORMAL)
            
            print("✅ Camera started successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {str(e)}")
            
    def stop_camera(self):
        """Stop camera capture"""
        self.detection_active = False
        
        if self.camera:
            self.camera.release()
            self.camera = None
            
        # Update button states
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.detect_button.config(state=tk.DISABLED)
        
        # Clear video display
        self.video_label.config(text="Camera stopped", image="")
        
        print("⏹️ Camera stopped")
        
    def toggle_detection(self):
        """Toggle object detection"""
        if not self.detection_active:
            self.detection_active = True
            self.detect_button.config(text="⏸️ Stop Detection", bg='#e67e22')
            
            # Start detection thread
            self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
            self.detection_thread.start()
            
            print("🔍 Detection started")
        else:
            self.detection_active = False
            self.detect_button.config(text="🔍 Start Detection", bg='#3498db')
            print("⏸️ Detection stopped")
            
    def camera_loop(self):
        """Optimized camera capture loop"""
        fps_counter = 0
        fps_start_time = time.time()
        
        while self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if not ret:
                break
                
            # Store frame for detection (only if detection is active)
            if self.detection_active:
                self.current_frame = frame.copy()
            
            # Update FPS counter
            fps_counter += 1
            if fps_counter % 30 == 0:  # Update every 30 frames
                fps_end_time = time.time()
                fps = 30 / (fps_end_time - fps_start_time)
                self.root.after(0, lambda: self.fps_label.config(text=f"Camera FPS: {fps:.1f}"))
                fps_start_time = fps_end_time
            
            # Draw detections on frame if available
            display_frame = frame.copy()
            if self.latest_detections:
                display_frame = self.draw_detections(display_frame, self.latest_detections)
            
            # Optimize image processing - resize before conversion
            display_frame = cv2.resize(display_frame, (640, 480))
            frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            frame_tk = ImageTk.PhotoImage(frame_pil)
            
            # Update video display
            self.root.after(0, lambda: self.video_label.config(image=frame_tk))
            self.root.after(0, lambda: setattr(self.video_label, 'image', frame_tk))
            
            time.sleep(0.02)  # ~50 FPS for smoother display
            
    def detection_loop(self):
        """Optimized object detection loop with frame skipping"""
        while self.detection_active and self.camera and self.camera.isOpened():
            if self.current_frame is not None and self.model is not None:
                try:
                    # Frame skipping for better performance
                    self.frame_skip_counter += 1
                    if self.frame_skip_counter <= self.frame_skip_interval:
                        time.sleep(0.05)  # Faster loop when skipping frames
                        continue
                    self.frame_skip_counter = 0
                    
                    # Resize frame for faster processing
                    detection_frame = cv2.resize(self.current_frame, (416, 416))
                    
                    # Run YOLO detection with optimized settings
                    results = self.model(detection_frame, verbose=False, conf=self.confidence_threshold)
                    result = results[0]
                    
                    # Process detections with confidence filtering
                    detections = []
                    if result.boxes is not None:
                        boxes = result.boxes.xyxy.cpu().numpy()
                        confidences = result.boxes.conf.cpu().numpy()
                        class_ids = result.boxes.cls.cpu().numpy()
                        
                        for i in range(len(boxes)):
                            confidence = float(confidences[i])
                            if confidence >= self.confidence_threshold:
                                # Scale bounding box back to original frame size
                                scale_x = self.current_frame.shape[1] / 416
                                scale_y = self.current_frame.shape[0] / 416
                                
                                detection = {
                                    'bbox': boxes[i] * [scale_x, scale_y, scale_x, scale_y],
                                    'confidence': confidence,
                                    'class_id': int(class_ids[i]),
                                    'class_name': self.model.names[int(class_ids[i])]
                                }
                                detections.append(detection)
                    
                    # Store latest detections for drawing
                    self.latest_detections = detections
                    
                    # Update detection FPS
                    self.detection_fps_counter += 1
                    if self.detection_fps_counter % 10 == 0:
                        detection_fps_end_time = time.time()
                        detection_fps = 10 / (detection_fps_end_time - self.detection_fps_start_time)
                        self.root.after(0, lambda: self.detection_fps_label.config(text=f"Detection FPS: {detection_fps:.1f}"))
                        self.detection_fps_start_time = detection_fps_end_time
                    
                    # Update detection info
                    self.root.after(0, lambda: self.update_detection_info(detections))
                    
                except Exception as e:
                    print(f"Detection error: {e}")
                    
            time.sleep(0.05)  # Faster detection loop
            
    def draw_detections(self, frame, detections):
        """Optimized drawing of bounding boxes and labels"""
        if not detections:
            return frame
            
        for detection in detections:
            bbox = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            
            # Extract coordinates
            x1, y1, x2, y2 = map(int, bbox)
            
            # Ensure coordinates are within frame bounds
            x1 = max(0, min(x1, frame.shape[1]))
            y1 = max(0, min(y1, frame.shape[0]))
            x2 = max(0, min(x2, frame.shape[1]))
            y2 = max(0, min(y2, frame.shape[0]))
            
            # Draw bounding box with thickness based on confidence
            thickness = max(1, int(3 * confidence))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), thickness)
            
            # Prepare label text (shorter for better performance)
            label = f"{class_name}: {confidence:.1f}"
            
            # Get text size for background rectangle
            font_scale = 0.5
            thickness_text = 1
            (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness_text)
            
            # Draw background rectangle for text
            cv2.rectangle(frame, (x1, y1 - text_height - 5), (x1 + text_width, y1), (0, 255, 0), -1)
            
            # Draw text
            cv2.putText(frame, label, (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness_text)
            
        return frame
    
    def update_detection_info(self, detections):
        """Update detection information in GUI"""
        # Update detection count
        self.detection_count_label.config(text=f"Detections: {len(detections)}")
        
        # Update detection list
        self.detection_listbox.delete(0, tk.END)
        for detection in detections:
            info = f"{detection['class_name']}: {detection['confidence']:.2f}"
            self.detection_listbox.insert(tk.END, info)
            
    def on_closing(self):
        """Handle window closing"""
        self.detection_active = False
        if self.camera:
            self.camera.release()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ObjectDetectionGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
