import os
import sys
from train_model import MarrakechClassifier
from finetune import fine_tune_model
from evaluate import evaluate_model
from prepare_data import prepare_dataset
from config import CONFIG, load_config
from utils import plot_training_history, count_parameters

def run_pipeline(stage="all"):
    """
    Run the complete ML pipeline for price classification
    Stages: prepare, train, finetune, evaluate, all
    """
    # Use combined data configuration
    data_dir = "../data/price_combined"
    model_path = "../models/price_efficientnet.h5"
    finetuned_path = "../models/price_efficientnet_finetuned.h5"
    
    # Stage 1: Prepare Data (Augmentation)
    if stage in ["prepare", "all"]:
        print("\n=== Stage 1: Preparing Data with Augmentation ===")
        if os.path.exists(data_dir):
            # Run data augmentation
            os.system("python augment_data.py")
            data_dir = "../data/price_augmented"  # Use augmented data
        else:
            print(f"Warning: {data_dir} not found. Skipping data preparation.")
    
    # Stage 2: Train Model
    if stage in ["train", "all"]:
        print("\n=== Stage 2: Training Price Classification Model ===")
        
        # Use augmented data if available
        train_data_dir = "../data/price_augmented" if os.path.exists("../data/price_augmented") else data_dir
        
        if os.path.exists(train_data_dir):
            # Use the price training script
            os.system("python train_price_model.py --data " + train_data_dir + " --epochs 50 --batch 16")
        else:
            print(f"Error: Data directory {train_data_dir} not found.")
            return
    
    # Stage 3: Fine-tune Model
    if stage in ["finetune", "all"]:
        print("\n=== Stage 3: Fine-tuning Complete ===")
        print("Fine-tuning is included in the training script.")
    
    # Stage 4: Evaluate Model
    if stage in ["evaluate", "all"]:
        print("\n=== Stage 4: Evaluating Model ===")
        test_dir = os.path.join(data_dir, "test")
        if os.path.exists(test_dir):
            os.system("python evaluate_model.py")
        else:
            print(f"Warning: Test directory {test_dir} not found.")
    
    print("\n=== Pipeline Complete ===")

if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if stage not in ["prepare", "train", "finetune", "evaluate", "all"]:
        print(f"Invalid stage: {stage}")
        print("Valid stages: prepare, train, finetune, evaluate, all")
        sys.exit(1)
    
    run_pipeline(stage)