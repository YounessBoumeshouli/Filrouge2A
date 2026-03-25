"""
Metrics for YOLO model evaluation
"""

import numpy as np
import torch

def compute_ap(recall, precision):
    """
    Compute Average Precision (AP) from recall and precision curves
    
    Args:
        recall: Array of recall values
        precision: Array of precision values
    
    Returns:
        ap: Average precision
    """
    # Append sentinel values
    mrec = np.concatenate(([0.], recall, [1.]))
    mpre = np.concatenate(([1.], precision, [0.]))
    
    # Compute precision envelope
    for i in range(mpre.size - 1, 0, -1):
        mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])
    
    # Calculate area under curve
    i = np.where(mrec[1:] != mrec[:-1])[0]
    ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    
    return ap

def compute_iou(box1, box2):
    """
    Compute Intersection over Union (IoU) between two boxes
    
    Args:
        box1: [x1, y1, x2, y2]
        box2: [x1, y1, x2, y2]
    
    Returns:
        iou: IoU value
    """
    x1_inter = max(box1[0], box2[0])
    y1_inter = max(box1[1], box2[1])
    x2_inter = min(box1[2], box2[2])
    y2_inter = min(box1[3], box2[3])
    
    if x2_inter < x1_inter or y2_inter < y1_inter:
        return 0.0
    
    inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)
    
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    union_area = box1_area + box2_area - inter_area
    
    return inter_area / union_area if union_area > 0 else 0.0

def compute_metrics(predictions, targets, iou_threshold=0.5):
    """
    Compute precision, recall, and mAP
    
    Args:
        predictions: List of [x1, y1, x2, y2, conf, class_id]
        targets: List of [x1, y1, x2, y2, class_id]
        iou_threshold: IoU threshold for positive detection
    
    Returns:
        metrics: Dict with precision, recall, mAP
    """
    tp = np.zeros(len(predictions))
    fp = np.zeros(len(predictions))
    
    target_count = {}
    for target in targets:
        class_id = int(target[4])
        target_count[class_id] = target_count.get(class_id, 0) + 1
    
    # Sort predictions by confidence
    predictions = sorted(predictions, key=lambda x: x[4], reverse=True)
    
    for i, pred in enumerate(predictions):
        pred_box = pred[:4]
        pred_conf = pred[4]
        pred_class = int(pred[5])
        
        best_iou = 0
        best_target_idx = -1
        
        for j, target in enumerate(targets):
            if int(target[4]) == pred_class:
                target_box = target[:4]
                iou = compute_iou(pred_box, target_box)
                
                if iou > best_iou:
                    best_iou = iou
                    best_target_idx = j
        
        if best_iou >= iou_threshold and best_target_idx >= 0:
            tp[i] = 1
            targets.pop(best_target_idx)
        else:
            fp[i] = 1
    
    # Compute precision and recall
    tp_cumsum = np.cumsum(tp)
    fp_cumsum = np.cumsum(fp)
    
    recalls = tp_cumsum / (sum(target_count.values()) + 1e-6)
    precisions = tp_cumsum / (tp_cumsum + fp_cumsum + 1e-6)
    
    # Compute AP
    ap = compute_ap(recalls, precisions)
    
    return {
        'precision': precisions[-1] if len(precisions) > 0 else 0,
        'recall': recalls[-1] if len(recalls) > 0 else 0,
        'mAP': ap
    }

class MetricsTracker:
    """Track metrics during training"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.losses = []
        self.accuracies = []
    
    def update(self, loss, accuracy=None):
        self.losses.append(loss)
        if accuracy is not None:
            self.accuracies.append(accuracy)
    
    def get_average_loss(self):
        return np.mean(self.losses) if self.losses else 0
    
    def get_average_accuracy(self):
        return np.mean(self.accuracies) if self.accuracies else 0
