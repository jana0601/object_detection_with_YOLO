from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import base64
import io
import json

app = Flask(__name__)
CORS(app)

# Initialize YOLO model
model = YOLO('yolov8n.pt')  # Using nano version for faster inference

# Create uploads directory
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def process_image(image_path):
    """Process image with YOLO model and return detection results"""
    try:
        # Run YOLO detection
        results = model(image_path)
        
        # Get the first result
        result = results[0]
        
        # Extract detection data
        detections = []
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()  # Get bounding boxes
            confidences = result.boxes.conf.cpu().numpy()  # Get confidences
            class_ids = result.boxes.cls.cpu().numpy()  # Get class IDs
            
            for i in range(len(boxes)):
                detection = {
                    'bbox': boxes[i].tolist(),
                    'confidence': float(confidences[i]),
                    'class_id': int(class_ids[i]),
                    'class_name': model.names[int(class_ids[i])]
                }
                detections.append(detection)
        
        # Save annotated image
        annotated_img = result.plot()
        result_path = os.path.join(app.config['RESULTS_FOLDER'], f'result_{os.path.basename(image_path)}')
        cv2.imwrite(result_path, annotated_img)
        
        return {
            'success': True,
            'detections': detections,
            'result_image': result_path,
            'total_detections': len(detections)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    return send_from_directory('frontend/build', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('frontend/build/static', filename)

@app.route('/api/detect', methods=['POST'])
def detect_objects():
    """API endpoint for object detection"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        if file:
            # Save uploaded file
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Process image
            result = process_image(file_path)
            
            if result['success']:
                # Convert result image to base64 for frontend
                with open(result['result_image'], 'rb') as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                
                return jsonify({
                    'success': True,
                    'detections': result['detections'],
                    'result_image': f"data:image/jpeg;base64,{img_base64}",
                    'total_detections': result['total_detections']
                })
            else:
                return jsonify({'error': result['error']}), 500
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model': 'YOLOv8'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
