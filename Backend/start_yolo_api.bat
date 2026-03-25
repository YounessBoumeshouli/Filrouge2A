@echo off
echo ========================================
echo    Starting YOLO API Server
echo ========================================
echo.

echo Installing dependencies...
pip install fastapi uvicorn ultralytics opencv-python pillow python-multipart numpy

echo.
echo Checking for trained model...
if not exist "models\ceramic_yolo_trained.pt" (
    echo ❌ Trained model not found!
    echo Please copy the model from Docker container first:
    echo   docker cp ceramic-yolo-trainer:/app/models/ceramic_yolo_trained.pt models/
    echo.
    pause
    exit /b 1
)

echo ✅ Model found
echo.

echo Starting YOLO API server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python yolo_api.py