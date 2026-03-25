@echo off
echo ========================================
echo YOLO-Nano Dataset Preparation
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Step 1: Analyzing current dataset structure...
echo ----------------------------------------
python analyze_dataset.py --dataset ../../marrakech_dataset_enhanced

echo.
echo Step 2: Preparing YOLO dataset...
echo ----------------------------------------
python prepare_yolo_dataset.py --source ../../marrakech_dataset_enhanced --output data/yolo_dataset

echo.
echo Step 3: Verifying prepared dataset...
echo ----------------------------------------
python analyze_dataset.py --dataset data/yolo_dataset

echo.
echo ========================================
echo Dataset preparation completed!
echo.
echo Next steps:
echo 1. Review the generated dataset in data/yolo_dataset/
echo 2. Update training configuration if needed
echo 3. Start training with: python train.py --data data/yolo_dataset/dataset.yaml
echo ========================================
pause