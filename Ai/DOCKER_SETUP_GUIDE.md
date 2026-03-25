# Docker YOLO Training Setup Guide

## 🐳 Prerequisites

### 1. Install Docker Desktop
- Download from: https://www.docker.com/products/docker-desktop
- Install and start Docker Desktop
- Ensure Docker is running (check system tray)

### 2. Verify Installation
```bash
docker --version
docker-compose --version
```

## 📁 File Structure
```
Ai/
├── Dockerfile                 # Docker image definition
├── docker-compose.yml        # Container orchestration
├── docker_train.py           # Training script for container
├── run_docker_training.bat   # Windows batch script
├── run_docker_training.ps1   # PowerShell script
├── data/
│   └── ceramic_simple/       # Your prepared dataset
│       ├── dataset.yaml
│       ├── images/
│       │   ├── train/
│       │   └── val/
│       └── labels/
│           ├── train/
│           └── val/
├── models/                   # Output directory (will be created)
└── runs/                     # Training logs (will be created)
```

## 🚀 Quick Start

### Option 1: Using Batch Script (Recommended)
```bash
# Navigate to the Ai directory
cd c:\Users\boume\Briefs\Filrouge2A\Ai

# Run the training
run_docker_training.bat
```

### Option 2: Using PowerShell
```powershell
# Navigate to the Ai directory
cd c:\Users\boume\Briefs\Filrouge2A\Ai

# Run the training
.\run_docker_training.ps1
```

### Option 3: Manual Docker Commands
```bash
# Build the image
docker build -t ceramic-yolo-trainer .

# Run with Docker Compose
docker-compose up --build

# OR run directly
docker run -v "%cd%\data\ceramic_simple:/app/data:ro" -v "%cd%\models:/app/models" -v "%cd%\runs:/app/runs" ceramic-yolo-trainer
```

## 📊 What Happens During Training

1. **Container Setup**: Docker builds the image with all dependencies
2. **Dataset Mount**: Your dataset is mounted read-only to `/app/data`
3. **Model Training**: YOLO trains for 50 epochs with augmentation
4. **Model Export**: Trained model saved to `models/ceramic_yolo_trained.pt`
5. **Results Export**: Training logs and metrics saved to `runs/`

## 🔧 Configuration

### Training Parameters (in docker_train.py)
```python
training_params = {
    'epochs': 50,           # Number of training epochs
    'imgsz': 640,          # Image size
    'batch': 8,            # Batch size (auto-adjusted for CPU)
    'patience': 20,        # Early stopping patience
    
    # Augmentation
    'hsv_h': 0.015,        # HSV hue augmentation
    'hsv_s': 0.7,          # HSV saturation
    'hsv_v': 0.4,          # HSV value
    'degrees': 10,         # Rotation degrees
    'translate': 0.1,      # Translation
    'fliplr': 0.5,         # Horizontal flip probability
    'mosaic': 1.0,         # Mosaic augmentation
    'mixup': 0.1,          # MixUp augmentation
}
```

### GPU Support (Optional)
If you have NVIDIA GPU with Docker GPU support:

1. Install NVIDIA Container Toolkit
2. Uncomment GPU section in `docker-compose.yml`:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

## 📈 Expected Output

### During Training
```
🐳 YOLO Training in Docker Container
==================================================
📊 Dataset found: /app/data/dataset.yaml
🖥️ Using device: cpu
🔄 Loading YOLO model...
🚀 Starting training with parameters:
   epochs: 50
   batch: 4
   device: cpu
   ...

🔥 Training started...
Epoch 1/50: 100%|██████████| 59/59 [02:15<00:00,  2.29s/it]
      Class     Images  Instances      Box(P          R      mAP50  mAP50-95)
        all        60        60      0.756      0.683      0.742      0.421
...
```

### After Training
```
✅ Model saved to: /app/models/ceramic_yolo_trained.pt
📊 Training results saved to: /app/models/training_results
🎉 TRAINING COMPLETED SUCCESSFULLY!
```

## 📁 Output Files

After training, you'll find:

### `models/ceramic_yolo_trained.pt`
- Your trained YOLO model
- Ready for inference
- Can be used with `YOLO('path/to/model.pt')`

### `models/training_results/`
- Complete training logs
- Performance metrics
- Training curves
- Validation results

### `runs/train/ceramic_docker/`
- Detailed training logs
- Loss curves
- Confusion matrices
- Sample predictions

## 🧪 Testing Your Model

After training, test your model:

```python
from ultralytics import YOLO

# Load your trained model
model = YOLO('models/ceramic_yolo_trained.pt')

# Run inference
results = model('path/to/test/image.jpg')

# Display results
results[0].show()
```

## 🔧 Troubleshooting

### Docker Issues
```bash
# Check Docker status
docker info

# View container logs
docker logs ceramic-yolo-trainer

# Clean up containers
docker-compose down
docker system prune
```

### Memory Issues
- Reduce batch size in `docker_train.py`
- Close other applications
- Increase Docker memory limit in Docker Desktop settings

### Dataset Issues
- Ensure `data/ceramic_simple/dataset.yaml` exists
- Check file permissions
- Verify dataset structure

## 🎯 Advantages of Docker Training

✅ **Clean Environment**: No dependency conflicts
✅ **Reproducible**: Same results every time
✅ **Isolated**: Won't affect your system
✅ **Portable**: Works on any Docker-enabled system
✅ **No MLflow Issues**: Completely bypassed
✅ **Easy Cleanup**: Just remove container

## 📞 Support

If you encounter issues:
1. Check Docker Desktop is running
2. Verify dataset structure
3. Check container logs: `docker logs ceramic-yolo-trainer`
4. Ensure sufficient disk space (>5GB free)

Your dataset is ready and the Docker setup will handle all the MLflow issues automatically!