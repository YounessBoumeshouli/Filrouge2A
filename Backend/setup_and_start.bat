@echo off
echo ========================================
echo    Setting up YOLO Backend
echo ========================================
echo.

echo Step 1: Creating models directory...
if not exist "models" mkdir models

echo Step 2: Copying trained model from Docker container...
docker cp ceramic-yolo-trainer:/app/models/ceramic_yolo_trained.pt models/ceramic_yolo_trained.pt

if %errorlevel% equ 0 (
    echo ✅ Model copied successfully!
) else (
    echo ❌ Failed to copy model. Make sure Docker container exists.
    echo Try running: docker ps -a | findstr ceramic-yolo-trainer
    pause
    exit /b 1
)

echo.
echo Step 3: Installing Python dependencies...
pip install fastapi uvicorn ultralytics opencv-python pillow python-multipart numpy

echo.
echo Step 4: Starting YOLO API server...
echo 🚀 API will be available at: http://localhost:8000
echo 📚 API docs will be at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python yolo_api.py