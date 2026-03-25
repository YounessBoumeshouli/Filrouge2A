# Marrakech Monument Classification with EfficientNet

This project uses EfficientNet for classifying monuments and landmarks in Marrakech from images.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Organize your dataset:
```
data/
├── marrakech/
│   ├── Jemaa_el_Fnaa/
│   ├── Koutoubia_Mosque/
│   ├── Bahia_Palace/
│   └── ...
└── test/
    ├── Jemaa_el_Fnaa/
    ├── Koutoubia_Mosque/
    └── ...
```

## Usage

### Training
```bash
python train_model.py
```

### Prediction
```bash
python predict.py
```

### Evaluation
```bash
python evaluate.py
```

## Model Architecture

- **Backbone**: EfficientNet-B0 (pretrained on ImageNet)
- **Transfer Learning**: Frozen base + custom classification head
- **Input Size**: 224x224 RGB images
- **Output**: 10 monument classes with confidence scores

## Classes
1. Jemaa el-Fnaa
2. Koutoubia Mosque
3. Bahia Palace
4. Saadian Tombs
5. Ben Youssef Madrasa
6. Majorelle Garden
7. Menara Gardens
8. El Badi Palace
9. Agdal Gardens
10. Marrakech Medina

## Features
- Data augmentation for better generalization
- Early stopping and learning rate reduction
- Confidence scores for predictions
- Batch prediction support
- Model evaluation with confusion matrix