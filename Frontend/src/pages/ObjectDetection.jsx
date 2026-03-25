import React from 'react';
import YoloDetection from '../components/YoloDetection';
import '../ObjectDetection.css';

const ObjectDetection = () => {
  return (
    <div className="object-detection-page">
      <div className="page-header">
        <h1>🎯 Object Detection</h1>
        <p>Discover monuments and products in your Marrakech photos using AI</p>
      </div>
      
      <YoloDetection />
      
      <div className="page-footer">
        <div className="info-section">
          <h3>How it works</h3>
          <div className="info-grid">
            <div className="info-item">
              <div className="info-icon">📷</div>
              <h4>Upload Image</h4>
              <p>Select a photo from your device containing Marrakech scenes</p>
            </div>
            <div className="info-item">
              <div className="info-icon">🤖</div>
              <h4>AI Analysis</h4>
              <p>Our YOLO-Nano model analyzes the image for monuments and products</p>
            </div>
            <div className="info-item">
              <div className="info-icon">🎯</div>
              <h4>Get Results</h4>
              <p>View detected objects with confidence scores and categories</p>
            </div>
          </div>
        </div>
        
        <div className="supported-objects">
          <h3>Supported Objects</h3>
          <div className="objects-grid">
            <div className="object-category">
              <h4>🏛️ Monuments</h4>
              <ul>
                <li>Jemaa el-Fnaa</li>
                <li>Koutoubia Mosque</li>
                <li>Bahia Palace</li>
                <li>Saadian Tombs</li>
                <li>Ben Youssef Madrasa</li>
                <li>Majorelle Garden</li>
                <li>Menara Gardens</li>
                <li>El Badi Palace</li>
                <li>Agdal Gardens</li>
                <li>Marrakech Medina</li>
              </ul>
            </div>
            <div className="object-category">
              <h4>🛍️ Products</h4>
              <ul>
                <li>Argan Oil</li>
                <li>Crafts</li>
                <li>Jewelry</li>
                <li>Lanterns</li>
                <li>Leather Goods</li>
                <li>Spices</li>
                <li>Textiles</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ObjectDetection;