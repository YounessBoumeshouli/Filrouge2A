"""
YOLO-Nano Detection Script
"""

import argparse
import cv2
import torch
import numpy as np
from pathlib import Path
import yaml

from utils.models import YOLONano
from utils.general import non_max_suppression, scale_coords, plot_one_box

class YOLODetector:
    """YOLO detector for inference"""
    
    def __init__(self, model_path, config_path, device=''):
        self.device = torch.device('cuda' if torch.cuda.is_available() and device != 'cpu' else 'cpu')
        
        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load model
        self.model = YOLONano(
            num_classes=self.config['data']['nc'],
            img_size=self.config['model']['input_size'][0]
        ).to(self.device)
        
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        
        self.img_size = self.config['model']['input_size'][0]
        self.class_names = self.config['data']['names']
        self.conf_thres = self.config['inference']['conf_thres']
        self.iou_thres = self.config['inference']['iou_thres']
    
    def preprocess(self, img_path):
        """Preprocess image"""
        img = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize
        h, w = img_rgb.shape[:2]
        img_resized = cv2.resize(img_rgb, (self.img_size, self.img_size))
        
        # Normalize
        img_tensor = torch.from_numpy(img_resized).float() / 255.0
        img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0).to(self.device)
        
        return img_tensor, img, (h, w)
    
    def detect(self, img_path, conf_thres=None, iou_thres=None):
        """Run detection"""
        conf_thres = conf_thres or self.conf_thres
        iou_thres = iou_thres or self.iou_thres
        
        img_tensor, img_orig, orig_shape = self.preprocess(img_path)
        
        with torch.no_grad():
            pred = self.model(img_tensor)
        
        # NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, max_det=100)
        
        detections = []
        if len(pred) > 0 and pred[0] is not None:
            det = pred[0]
            
            # Scale coordinates to original image
            det[:, :4] = scale_coords(
                (self.img_size, self.img_size), 
                det[:, :4], 
                orig_shape
            )
            
            for *xyxy, conf, cls in det:
                x1, y1, x2, y2 = [int(x.item()) for x in xyxy]
                confidence = conf.item()
                class_id = int(cls.item())
                class_name = self.class_names[class_id]
                
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': confidence,
                    'class_id': class_id,
                    'class_name': class_name
                })
        
        return detections, img_orig
    
    def visualize(self, img, detections, output_path=None):
        """Visualize detections"""
        img_vis = img.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            class_name = det['class_name']
            
            label = f'{class_name} {conf:.2f}'
            color = (0, 255, 0)
            
            plot_one_box([x1, y1, x2, y2], img_vis, color=color, label=label)
        
        if output_path:
            cv2.imwrite(output_path, img_vis)
        
        return img_vis

def main():
    parser = argparse.ArgumentParser(description='YOLO-Nano Detection')
    parser.add_argument('--model', type=str, required=True, help='Path to model checkpoint')
    parser.add_argument('--config', type=str, default='configs/yolo_nano.yaml', help='Path to config')
    parser.add_argument('--source', type=str, required=True, help='Image or directory path')
    parser.add_argument('--output', type=str, default='runs/detect', help='Output directory')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='Confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='IoU threshold')
    parser.add_argument('--device', type=str, default='', help='Device (cuda/cpu)')
    
    args = parser.parse_args()
    
    # Create detector
    detector = YOLODetector(args.model, args.config, args.device)
    
    # Create output directory
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    # Process images
    source_path = Path(args.source)
    
    if source_path.is_file():
        image_files = [source_path]
    else:
        image_files = list(source_path.glob('*.jpg')) + list(source_path.glob('*.png'))
    
    for img_path in image_files:
        print(f'Processing {img_path}...')
        
        detections, img = detector.detect(str(img_path), args.conf_thres, args.iou_thres)
        
        print(f'  Found {len(detections)} objects')
        for det in detections:
            print(f'    {det["class_name"]}: {det["confidence"]:.2f}')
        
        # Visualize
        output_file = Path(args.output) / img_path.name
        detector.visualize(img, detections, str(output_file))
        print(f'  Saved to {output_file}')

if __name__ == '__main__':
    main()
