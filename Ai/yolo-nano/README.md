# YOLO-Nano for Marrakech Object Detection

Ultra-lightweight YOLO implementation for detecting monuments and products in Marrakech scenes.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Dataset

```bash
python prepare_dataset.py
```

This will organize images from `marrakech_dataset_enhanced` into YOLO format:
- `data/train/` - Training images and labels
- `data/val/` - Validation images and labels
- `data/test/` - Test images and labels

## Training

### Basic Training

```bash
python train.py --epochs 100 --batch-size 16 --img-size 416
```

### Advanced Options

```bash
python train.py \
    --config configs/yolo_nano.yaml \
    --data data/dataset.yaml \
    --epochs 100 \
    --batch-size 16 \
    --img-size 416 \
    --device cuda \
    --workers 4 \
    --project runs/train \
    --name exp1 \
    --wandb
```

### Resume Training

```bash
python train.py --resume runs/train/exp1/best.pt
```

## Inference

### Detect Objects in Image

```bash
python detect.py \
    --model runs/train/exp1/best.pt \
    --source path/to/image.jpg \
    --output runs/detect
```

### Detect in Directory

```bash
python detect.py \
    --model runs/train/exp1/best.pt \
    --source path/to/images/ \
    --output runs/detect
```

## Model Architecture

YOLO-Nano uses:
- **Backbone**: ShuffleNet-based architecture with depthwise separable convolutions
- **Neck**: Feature pyramid network for multi-scale detection
- **Head**: Detection heads for 3 scales (8x, 16x, 32x)

### Model Size
- Parameters: ~1.2M
- Model size: ~5MB (float32)
- Inference speed: ~50ms on CPU, ~5ms on GPU

## Classes (18 total)

### Monuments (0-9)
- jemaa_el_fnaa
- koutoubia_mosque
- bahia_palace
- saadian_tombs
- ben_youssef_madrasa
- majorelle_garden
- menara_gardens
- el_badi_palace
- agdal_gardens
- marrakech_medina

### Products (10-17)
- argan
- crafts
- jewelry
- lanterns
- leather
- price_tags
- spices
- textiles

## Configuration

Edit `configs/yolo_nano.yaml` to customize:
- Model architecture (width_multiple, depth_multiple)
- Training parameters (learning rate, momentum, weight decay)
- Augmentation settings
- Loss weights

## Output Structure

```
runs/
├── train/
│   └── exp1/
│       ├── best.pt          # Best model checkpoint
│       ├── epoch_10.pt      # Periodic checkpoints
│       └── events.out.tfevents  # TensorBoard logs
└── detect/
    └── image_with_detections.jpg
```

## Tips for Better Performance

1. **Data Quality**: Ensure images are well-labeled with accurate bounding boxes
2. **Augmentation**: Adjust augmentation parameters in config for your dataset
3. **Learning Rate**: Start with 0.01 and reduce if loss doesn't converge
4. **Batch Size**: Use larger batches (32-64) if GPU memory allows
5. **Epochs**: Train for at least 100 epochs for good convergence

## Troubleshooting

### Out of Memory
- Reduce batch size: `--batch-size 8`
- Reduce image size: `--img-size 320`

### Poor Detection
- Check data quality and labels
- Increase training epochs
- Adjust confidence threshold: `--conf-thres 0.3`

### Slow Training
- Use GPU: `--device cuda`
- Reduce number of workers: `--workers 2`

## References

- YOLO: You Only Look Once - https://arxiv.org/abs/1506.02640
- ShuffleNet - https://arxiv.org/abs/1707.01083
- Depthwise Separable Convolutions - https://arxiv.org/abs/1704.04861
