#  YOLO Object Detection Application

A modern web application for real-time object detection using YOLOv8, built with Flask backend and React frontend.
## Interface
![YOLO Object Detection Interface](https://github.com/jana0601/object_detection_with_YOLO/blob/main/interface2.jpg?raw=true)

##  Features

- **Real-time Object Detection**: Uses YOLOv8 nano model for fast and accurate detection
- **Modern UI**: Beautiful, responsive interface with gradient backgrounds and smooth animations
- **File Upload**: Drag-and-drop or click to upload images
- **Visual Results**: Side-by-side comparison of original and detected images
- **Detailed Detection Info**: Shows detected objects with confidence scores and bounding boxes
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Error Handling**: Comprehensive error handling and user feedback

##  Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd object_detection
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install React dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Build the React frontend**
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`



##  API Endpoints

### `POST /api/detect`
Upload an image for object detection.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: `image` (file)

**Response:**
```json
{
  "success": true,
  "detections": [
    {
      "bbox": [x1, y1, x2, y2],
      "confidence": 0.85,
      "class_id": 0,
      "class_name": "person"
    }
  ],
  "result_image": "data:image/jpeg;base64,...",
  "total_detections": 1
}
```

### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model": "YOLOv8"
}
```


##  Configuration

### Model Configuration
The application uses YOLOv8 nano model by default. You can modify the model in `app.py`:

```python
# Change model size
model = YOLO('yolov8s.pt')  # Small
model = YOLO('yolov8m.pt')  # Medium
model = YOLO('yolov8l.pt')  # Large
model = YOLO('yolov8x.pt')  # Extra Large
```

### File Size Limits
Default maximum file size is 16MB. Modify in `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

##  Deployment

### Using Docker
Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN cd frontend && npm install && npm run build

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```



