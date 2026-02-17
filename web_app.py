from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
import cv2
import base64
import numpy as np
from ultralytics import YOLO
import threading
import time
import json
import io
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yolo_detection_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
model = None
detection_active = False
latest_detections = []
confidence_threshold = 0.5

def load_model():
    """Load YOLO model"""
    global model
    try:
        model = YOLO('yolov8n.pt')
        print("✅ YOLO model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to load YOLO model: {e}")
        return False

def process_frame(frame_data):
    """Process frame for object detection and return annotated frame"""
    global model, confidence_threshold
    
    if model is None:
        return [], frame_data
    
    try:
        # Decode base64 image
        image_data = base64.b64decode(frame_data.split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Resize for faster processing
        frame_resized = cv2.resize(frame, (416, 416))
        
        # Run YOLO detection
        results = model(frame_resized, verbose=False, conf=confidence_threshold)
        result = results[0]
        
        # Process detections
        detections = []
        annotated_frame = frame.copy()
        
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy()
            
            # Scale back to original frame size
            scale_x = frame.shape[1] / 416
            scale_y = frame.shape[0] / 416
            
            for i in range(len(boxes)):
                confidence = float(confidences[i])
                if confidence >= confidence_threshold:
                    # Scale bounding box coordinates
                    x1, y1, x2, y2 = boxes[i] * [scale_x, scale_y, scale_x, scale_y]
                    
                    detection = {
                        'bbox': [x1, y1, x2, y2],
                        'confidence': confidence,
                        'class_id': int(class_ids[i]),
                        'class_name': model.names[int(class_ids[i])]
                    }
                    detections.append(detection)
                    
                    # Draw bounding box and label on frame
                    annotated_frame = draw_detection_on_frame(annotated_frame, detection)
        
        # Convert annotated frame back to base64
        annotated_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        annotated_pil = Image.fromarray(annotated_rgb)
        
        # Convert to base64
        buffer = io.BytesIO()
        annotated_pil.save(buffer, format='JPEG', quality=85)
        annotated_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        annotated_data_url = f"data:image/jpeg;base64,{annotated_base64}"
        
        return detections, annotated_data_url
        
    except Exception as e:
        print(f"Detection error: {e}")
        return [], frame_data

def draw_detection_on_frame(frame, detection):
    """Draw bounding box and label on frame"""
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
    thickness = max(2, int(4 * confidence))
    color = (0, 255, 0)  # Green color
    
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
    
    # Prepare label text
    label = f"{class_name}: {confidence:.2f}"
    
    # Get text size for background rectangle
    font_scale = 0.7
    thickness_text = 2
    (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness_text)
    
    # Draw background rectangle for text
    cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
    
    # Draw text
    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness_text)
    
    return frame

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/detect', methods=['POST'])
def detect_objects():
    """API endpoint for object detection"""
    global detection_active, latest_detections
    
    try:
        data = request.get_json()
        frame_data = data.get('frame')
        
        if not frame_data:
            return jsonify({'error': 'No frame data provided'}), 400
        
        if detection_active:
            detections, annotated_frame = process_frame(frame_data)
            latest_detections = detections
            
            # Emit real-time updates via WebSocket
            socketio.emit('detection_update', {
                'detections': detections,
                'count': len(detections),
                'annotated_frame': annotated_frame,
                'timestamp': time.time()
            })
            
            return jsonify({
                'success': True,
                'detections': detections,
                'count': len(detections),
                'annotated_frame': annotated_frame
            })
        else:
            return jsonify({
                'success': True,
                'detections': [],
                'count': 0,
                'annotated_frame': frame_data
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/toggle_detection', methods=['POST'])
def toggle_detection():
    """Toggle detection on/off"""
    global detection_active
    
    try:
        data = request.get_json()
        detection_active = data.get('active', False)
        
        socketio.emit('detection_status', {
            'active': detection_active,
            'timestamp': time.time()
        })
        
        return jsonify({
            'success': True,
            'active': detection_active
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/set_confidence', methods=['POST'])
def set_confidence():
    """Set confidence threshold"""
    global confidence_threshold
    
    try:
        data = request.get_json()
        confidence_threshold = float(data.get('confidence', 0.5))
        
        socketio.emit('confidence_update', {
            'confidence': confidence_threshold,
            'timestamp': time.time()
        })
        
        return jsonify({
            'success': True,
            'confidence': confidence_threshold
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """Get current status"""
    return jsonify({
        'detection_active': detection_active,
        'confidence_threshold': confidence_threshold,
        'model_loaded': model is not None,
        'latest_detections': latest_detections
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('status', {
        'detection_active': detection_active,
        'confidence_threshold': confidence_threshold,
        'model_loaded': model is not None
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

if __name__ == '__main__':
    # Load YOLO model
    if load_model():
        print("🚀 Starting YOLO Web Detection Server...")
        print("📱 Open your browser and go to: http://localhost:5000")
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Failed to start server - YOLO model not loaded")
