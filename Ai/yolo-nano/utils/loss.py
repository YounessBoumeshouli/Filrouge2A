"""
YOLO Loss Function
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class YOLOLoss(nn.Module):
    """YOLO Loss combining box, objectness, and classification losses"""
    
    def __init__(self, num_classes=18, anchors=None, img_size=416):
        super().__init__()
        self.num_classes = num_classes
        self.img_size = img_size
        
        self.lambda_box = 0.05
        self.lambda_obj = 1.0
        self.lambda_cls = 0.5
        
        self.bce_loss = nn.BCEWithLogitsLoss(reduction='mean')
        self.mse_loss = nn.MSELoss(reduction='mean')
    
    def forward(self, predictions, targets):
        """
        Args:
            predictions: List of 3 tensors [B, anchors*(5+classes), H, W] for each scale
            targets: [B, max_objects, 6] where 6 = [batch_idx, class, x, y, w, h]
        """
        total_loss = 0.0
        num_scales = len(predictions)
        
        for scale_idx, pred in enumerate(predictions):
            batch_size, num_channels, grid_h, grid_w = pred.shape
            num_anchors = 3
            
            # Reshape predictions: [B, anchors*(5+classes), H, W] -> [B, anchors, H, W, 5+classes]
            pred = pred.view(batch_size, num_anchors, 5 + self.num_classes, grid_h, grid_w)
            pred = pred.permute(0, 1, 3, 4, 2).contiguous()  # [B, anchors, H, W, 5+classes]
            
            # Extract predictions
            pred_xy = torch.sigmoid(pred[..., 0:2])      # Center coordinates
            pred_wh = pred[..., 2:4]                      # Width and height (log space)
            pred_conf = pred[..., 4]                      # Objectness (logits)
            pred_cls = pred[..., 5:]                      # Class logits
            
            # Create target tensors
            target_xy = torch.zeros_like(pred_xy)
            target_wh = torch.zeros_like(pred_wh)
            target_conf = torch.zeros_like(pred_conf)
            target_cls = torch.zeros_like(pred_cls)
            obj_mask = torch.zeros_like(pred_conf)
            
            # Process targets
            for b in range(batch_size):
                batch_targets = targets[targets[:, 0] == b]
                
                if len(batch_targets) > 0:
                    for target in batch_targets:
                        _, cls_id, x, y, w, h = target
                        
                        # Get grid cell
                        grid_x = int(x * grid_w)
                        grid_y = int(y * grid_h)
                        
                        if 0 <= grid_x < grid_w and 0 <= grid_y < grid_h:
                            # Assign to first anchor (simplified)
                            anchor_idx = 0
                            
                            # Target coordinates (relative to grid cell)
                            target_xy[b, anchor_idx, grid_y, grid_x, 0] = x * grid_w - grid_x
                            target_xy[b, anchor_idx, grid_y, grid_x, 1] = y * grid_h - grid_y
                            
                            # Target width and height
                            target_wh[b, anchor_idx, grid_y, grid_x, 0] = torch.log(w + 1e-6)
                            target_wh[b, anchor_idx, grid_y, grid_x, 1] = torch.log(h + 1e-6)
                            
                            # Target objectness and class
                            target_conf[b, anchor_idx, grid_y, grid_x] = 1.0
                            target_cls[b, anchor_idx, grid_y, grid_x, int(cls_id)] = 1.0
                            obj_mask[b, anchor_idx, grid_y, grid_x] = 1.0
            
            # Calculate losses
            # Box loss (only for cells with objects)
            if obj_mask.sum() > 0:
                box_loss_xy = self.mse_loss(pred_xy[obj_mask > 0], target_xy[obj_mask > 0])
                box_loss_wh = self.mse_loss(pred_wh[obj_mask > 0], target_wh[obj_mask > 0])
                box_loss = box_loss_xy + box_loss_wh
            else:
                box_loss = torch.tensor(0.0, device=pred.device)
            
            # Objectness loss
            obj_loss = self.bce_loss(pred_conf, target_conf)
            
            # Classification loss (only for cells with objects)
            if obj_mask.sum() > 0:
                cls_loss = self.bce_loss(pred_cls[obj_mask > 0], target_cls[obj_mask > 0])
            else:
                cls_loss = torch.tensor(0.0, device=pred.device)
            
            # Weighted total loss for this scale
            scale_loss = (self.lambda_box * box_loss + 
                         self.lambda_obj * obj_loss + 
                         self.lambda_cls * cls_loss)
            
            total_loss += scale_loss
        
        return total_loss / num_scales
