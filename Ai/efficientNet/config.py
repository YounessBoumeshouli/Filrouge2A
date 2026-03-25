import json
import os

CONFIG = {
    "model": {
        "architecture": "EfficientNetB0",
        "input_size": 224,
        "num_classes": 10,
        "pretrained": True,
        "weights": "imagenet"
    },
    "training": {
        "batch_size": 32,
        "epochs": 20,
        "learning_rate": 0.001,
        "optimizer": "Adam",
        "loss": "categorical_crossentropy",
        "metrics": ["accuracy"]
    },
    "finetuning": {
        "epochs": 15,
        "learning_rate": 0.0001,
        "unfreeze_layers": 50
    },
    "data_augmentation": {
        "rotation_range": 20,
        "width_shift_range": 0.2,
        "height_shift_range": 0.2,
        "horizontal_flip": True,
        "validation_split": 0.2
    },
    "callbacks": {
        "early_stopping_patience": 3,
        "reduce_lr_patience": 2,
        "reduce_lr_factor": 0.2
    },
    "classes": [
        "Jemaa_el_Fnaa",
        "Koutoubia_Mosque",
        "Bahia_Palace",
        "Saadian_Tombs",
        "Ben_Youssef_Madrasa",
        "Majorelle_Garden",
        "Menara_Gardens",
        "El_Badi_Palace",
        "Agdal_Gardens",
        "Marrakech_Medina"
    ],
    "paths": {
        "data_dir": "../data/marrakech",
        "model_save": "marrakech_efficientnet.h5",
        "finetuned_model": "marrakech_efficientnet_finetuned.h5",
        "logs_dir": "./logs"
    }
}

# ──────────────────────────────────────────────────────────
# Price Helper – Product Classification (8 Marrakech souk
# product categories scraped from Bing + Google images)
# ──────────────────────────────────────────────────────────
PRICE_CONFIG = {
    "model": {
        "architecture": "EfficientNetB0",
        "input_size": 224,
        "num_classes": 8,
        "pretrained": True,
        "weights": "imagenet"
    },
    "classes": [
        "argan",
        "crafts",
        "jewelry",
        "lanterns",
        "leather",
        "price_tags",
        "spices",
        "textiles"
    ],
    "training": {
        "batch_size": 16,
        "epochs": 25,
        "learning_rate": 0.001
    },
    "finetuning": {
        "epochs": 15,
        "learning_rate": 0.0001,
        "unfreeze_layers": 50
    },
    "data_augmentation": {
        "rotation_range": 30,
        "width_shift_range": 0.2,
        "height_shift_range": 0.2,
        "shear_range": 0.15,
        "zoom_range": 0.2,
        "horizontal_flip": True,
        "brightness_range": [0.8, 1.2]
    },
    "callbacks": {
        "early_stopping_patience": 5,
        "reduce_lr_patience": 3,
        "reduce_lr_factor": 0.3
    },
    "paths": {
        # raw dataset (bing/google sub-folders per category)
        "raw_dataset": "../../marrakech_dataset",
        # prepared split (train / val / test)
        "data_dir": "../data/price",
        "models_dir": "../models",
        "model_save": "../models/price_efficientnet.h5",
        "finetuned_model": "../models/price_efficientnet_finetuned.h5",
        "class_indices": "../models/price_class_indices.json",
        "logs_dir": "../models/logs"
    }
}

def load_config(config_path="config.json"):
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return CONFIG

def save_config(config, config_path="config.json"):
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

if __name__ == "__main__":
    save_config(CONFIG)
    print("Config saved!")