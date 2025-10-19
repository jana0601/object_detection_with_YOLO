import React, { useState, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      
      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      
      // Reset previous results
      setResultImage(null);
      setDetections([]);
    }
  };

  const handleDetect = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await axios.post('/api/detect', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setResultImage(response.data.result_image);
        setDetections(response.data.detections);
      } else {
        setError('Detection failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred during detection');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResultImage(null);
    setDetections([]);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#4CAF50'; // Green
    if (confidence >= 0.6) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔍 YOLO Object Detection</h1>
        <p>Upload an image to detect objects using YOLOv8</p>
      </header>

      <main className="App-main">
        <div className="upload-section">
          <div className="file-input-container">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept="image/*"
              className="file-input"
              id="file-input"
            />
            <label htmlFor="file-input" className="file-input-label">
              📁 Choose Image
            </label>
          </div>

          {selectedFile && (
            <div className="file-info">
              <p>Selected: {selectedFile.name}</p>
              <p>Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}

          <div className="button-group">
            <button
              onClick={handleDetect}
              disabled={!selectedFile || loading}
              className="detect-button"
            >
              {loading ? '🔄 Detecting...' : '🚀 Detect Objects'}
            </button>
            <button
              onClick={handleReset}
              className="reset-button"
            >
              🔄 Reset
            </button>
          </div>
        </div>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        <div className="results-section">
          {previewUrl && (
            <div className="image-container">
              <h3>Original Image</h3>
              <img src={previewUrl} alt="Original" className="preview-image" />
            </div>
          )}

          {resultImage && (
            <div className="image-container">
              <h3>Detection Results</h3>
              <img src={resultImage} alt="Detection Results" className="result-image" />
            </div>
          )}

          {detections.length > 0 && (
            <div className="detections-container">
              <h3>Detected Objects ({detections.length})</h3>
              <div className="detections-grid">
                {detections.map((detection, index) => (
                  <div key={index} className="detection-card">
                    <div className="detection-header">
                      <span className="class-name">{detection.class_name}</span>
                      <span 
                        className="confidence"
                        style={{ color: getConfidenceColor(detection.confidence) }}
                      >
                        {(detection.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="detection-details">
                      <p>Class ID: {detection.class_id}</p>
                      <p>Bounding Box: [{detection.bbox.map(b => b.toFixed(1)).join(', ')}]</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="App-footer">
        <p>Powered by YOLOv8 | Built with React & Flask</p>
      </footer>
    </div>
  );
}

export default App;
