"""
YOLO-Nano Model Architecture
Ultra-lightweight YOLO implementation for mobile deployment
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class ConvBNReLU(nn.Module):
    """Standard convolution with BatchNorm and ReLU"""
    def __init__(self, in_channels, out_channels, kernel_size=1, stride=1, padding=0, groups=1):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, groups=groups, bias=False)
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU6(inplace=True)
    
    def forward(self, x):
        return self.relu(self.bn(self.conv(x)))

class DepthwiseSeparableConv(nn.Module):
    """Depthwise separable convolution for efficiency"""
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=1):
        super().__init__()
        self.depthwise = nn.Conv2d(in_channels, in_channels, kernel_size, stride, padding, groups=in_channels, bias=False)
        self.pointwise = nn.Conv2d(in_channels, out_channels, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(in_channels)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU6(inplace=True)
    
    def forward(self, x):
        x = self.relu(self.bn1(self.depthwise(x)))
        x = self.relu(self.bn2(self.pointwise(x)))
        return x

class ShuffleBlock(nn.Module):
    """ShuffleNet block for channel shuffling"""
    def __init__(self, in_channels, out_channels, stride=1, groups=2):
        super().__init__()
        self.stride = stride
        self.groups = groups
        
        mid_channels = out_channels // 4
        
        self.conv1 = ConvBNReLU(in_channels, mid_channels, 1, groups=groups)
        self.conv2 = DepthwiseSeparableConv(mid_channels, mid_channels, 3, stride)
        self.conv3 = ConvBNReLU(mid_channels, out_channels, 1, groups=groups)
        
        if stride == 2:
            self.shortcut = nn.Sequential(
                DepthwiseSeparableConv(in_channels, in_channels, 3, stride),
                ConvBNReLU(in_channels, out_channels, 1, groups=groups)
            )
        elif in_channels != out_channels:
            self.shortcut = ConvBNReLU(in_channels, out_channels, 1)
        else:
            self.shortcut = nn.Identity()
    
    def forward(self, x):
        residual = self.shortcut(x)
        
        x = self.conv1(x)
        x = self.channel_shuffle(x)
        x = self.conv2(x)
        x = self.conv3(x)
        
        return F.relu(x + residual)
    
    def channel_shuffle(self, x):
        batch_size, channels, height, width = x.size()
        channels_per_group = channels // self.groups
        
        # Reshape and transpose
        x = x.view(batch_size, self.groups, channels_per_group, height, width)
        x = x.transpose(1, 2).contiguous()
        x = x.view(batch_size, channels, height, width)
        
        return x

class YOLONanoBackbone(nn.Module):
    """Ultra-lightweight backbone for YOLO-Nano"""
    def __init__(self, width_mult=0.25):
        super().__init__()
        
        # Calculate channel numbers based on width multiplier
        def _make_divisible(v, divisor=8):
            return max(divisor, int(v + divisor / 2) // divisor * divisor)
        
        channels = [32, 64, 128, 256, 512]
        channels = [_make_divisible(ch * width_mult) for ch in channels]
        
        # Stem
        self.stem = ConvBNReLU(3, channels[0], 3, 2, 1)
        
        # Stage 1
        self.stage1 = nn.Sequential(
            DepthwiseSeparableConv(channels[0], channels[1], 3, 2),
            ShuffleBlock(channels[1], channels[1])
        )
        
        # Stage 2
        self.stage2 = nn.Sequential(
            ShuffleBlock(channels[1], channels[2], 2),
            ShuffleBlock(channels[2], channels[2]),
            ShuffleBlock(channels[2], channels[2])
        )
        
        # Stage 3
        self.stage3 = nn.Sequential(
            ShuffleBlock(channels[2], channels[3], 2),
            ShuffleBlock(channels[3], channels[3]),
            ShuffleBlock(channels[3], channels[3]),
            ShuffleBlock(channels[3], channels[3])
        )
        
        # Stage 4
        self.stage4 = nn.Sequential(
            ShuffleBlock(channels[3], channels[4], 2),
            ShuffleBlock(channels[4], channels[4])
        )
        
        self.out_channels = channels
    
    def forward(self, x):
        x = self.stem(x)
        
        c1 = self.stage1(x)    # 1/4
        c2 = self.stage2(c1)   # 1/8
        c3 = self.stage3(c2)   # 1/16
        c4 = self.stage4(c3)   # 1/32
        
        return c2, c3, c4

class YOLONanoHead(nn.Module):
    """Detection head for YOLO-Nano"""
    def __init__(self, num_classes, c2_channels, c3_channels, c4_channels, anchors_per_scale=3, dropout_rate=0.2):
        super().__init__()
        self.num_classes = num_classes
        self.anchors_per_scale = anchors_per_scale
        self.num_outputs = anchors_per_scale * (5 + num_classes)
        
        # Add dropout for regularization
        self.dropout = nn.Dropout2d(p=dropout_rate)
        
        # Detection heads for different scales with additional conv layers
        self.head_large_conv = nn.Sequential(
            ConvBNReLU(c2_channels, c2_channels // 2, 3, 1, 1),
            nn.Dropout2d(p=dropout_rate),
            nn.Conv2d(c2_channels // 2, self.num_outputs, 1)
        )
        
        self.head_medium_conv = nn.Sequential(
            ConvBNReLU(c3_channels, c3_channels // 2, 3, 1, 1),
            nn.Dropout2d(p=dropout_rate),
            nn.Conv2d(c3_channels // 2, self.num_outputs, 1)
        )
        
        self.head_small_conv = nn.Sequential(
            ConvBNReLU(c4_channels, c4_channels // 2, 3, 1, 1),
            nn.Dropout2d(p=dropout_rate),
            nn.Conv2d(c4_channels // 2, self.num_outputs, 1)
        )
        
        # Upsampling for feature fusion
        self.upsample = nn.Upsample(scale_factor=2, mode='nearest')
        
        # Feature fusion layers with dropout
        self.fusion1 = nn.Sequential(
            ConvBNReLU(c3_channels + c2_channels, c3_channels, 1),
            nn.Dropout2d(p=dropout_rate)
        )
        self.fusion2 = nn.Sequential(
            ConvBNReLU(c4_channels + c3_channels, c4_channels, 1),
            nn.Dropout2d(p=dropout_rate)
        )
    
    def forward(self, features):
        c2, c3, c4 = features
        # c2: 1/8 scale (52x52)
        # c3: 1/16 scale (26x26)
        # c4: 1/32 scale (13x13)
        
        # Large objects (1/8 scale) - direct detection on c2
        out_large = self.head_large_conv(c2)
        
        # Medium objects (1/16 scale) - downsample c2 and fuse with c3
        p3 = F.max_pool2d(c2, kernel_size=2, stride=2)
        p3 = torch.cat([p3, c3], dim=1)
        p3 = self.fusion1(p3)
        out_medium = self.head_medium_conv(p3)
        
        # Small objects (1/32 scale) - downsample p3 and fuse with c4
        p4 = F.max_pool2d(p3, kernel_size=2, stride=2)
        p4 = torch.cat([p4, c4], dim=1)
        p4 = self.fusion2(p4)
        out_small = self.head_small_conv(p4)
        
        return [out_large, out_medium, out_small]

class YOLONano(nn.Module):
    """YOLO-Nano: Ultra-lightweight object detection model"""
    def __init__(self, num_classes=80, img_size=416, width_mult=0.25, dropout_rate=0.2):
        super().__init__()
        self.num_classes = num_classes
        self.img_size = img_size
        
        # Backbone
        self.backbone = YOLONanoBackbone(width_mult)
        
        # Get backbone output channels
        # backbone.out_channels = [c0, c1, c2, c3, c4] = [8, 16, 32, 64, 128]
        # backbone returns c2, c3, c4 which are at indices 2, 3, 4
        backbone_channels = self.backbone.out_channels
        c2_ch = backbone_channels[2]  # 1/8 scale (32 channels)
        c3_ch = backbone_channels[3]  # 1/16 scale (64 channels)
        c4_ch = backbone_channels[4]  # 1/32 scale (128 channels)
        
        # Detection head with dropout
        self.head = YOLONanoHead(num_classes, c2_ch, c3_ch, c4_ch, dropout_rate=dropout_rate)
        
        # Initialize weights
        self._initialize_weights()
    
    def forward(self, x):
        # Extract features
        features = self.backbone(x)
        
        # Detection
        outputs = self.head(features)
        
        if self.training:
            return outputs
        else:
            # Inference mode - apply sigmoid and reshape
            inference_outputs = []
            for i, out in enumerate(outputs):
                batch_size, _, height, width = out.shape
                
                # Reshape: [B, anchors*(5+classes), H, W] -> [B, anchors, H, W, 5+classes]
                out = out.view(batch_size, 3, 5 + self.num_classes, height, width)
                out = out.permute(0, 1, 3, 4, 2).contiguous()
                
                # Apply sigmoid to objectness and class predictions
                out[..., 4:] = torch.sigmoid(out[..., 4:])
                
                # Reshape for NMS: [B, anchors*H*W, 5+classes]
                out = out.view(batch_size, -1, 5 + self.num_classes)
                inference_outputs.append(out)
            
            # Concatenate all scales
            return torch.cat(inference_outputs, dim=1)
    
    def _initialize_weights(self):
        """Initialize model weights"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
    
    def get_model_info(self):
        """Get model information"""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        return {
            'total_params': total_params,
            'trainable_params': trainable_params,
            'model_size_mb': total_params * 4 / (1024 * 1024),  # Assuming float32
            'num_classes': self.num_classes,
            'input_size': self.img_size
        }

def create_yolo_nano(num_classes=80, img_size=416, width_mult=0.25, dropout_rate=0.2):
    """Create YOLO-Nano model"""
    model = YOLONano(num_classes, img_size, width_mult, dropout_rate)
    return model

if __name__ == '__main__':
    # Test model
    model = create_yolo_nano(num_classes=18, img_size=416)
    
    # Print model info
    info = model.get_model_info()
    print("YOLO-Nano Model Information:")
    print(f"Total parameters: {info['total_params']:,}")
    print(f"Trainable parameters: {info['trainable_params']:,}")
    print(f"Model size: {info['model_size_mb']:.2f} MB")
    print(f"Number of classes: {info['num_classes']}")
    print(f"Input size: {info['input_size']}")
    
    # Test forward pass
    x = torch.randn(1, 3, 416, 416)
    model.eval()
    with torch.no_grad():
        outputs = model(x)
        print(f"Output shape: {outputs.shape}")
