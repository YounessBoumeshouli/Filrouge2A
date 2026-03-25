# Dockerfile for YOLO Training
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    ultralytics \
    torch \
    torchvision \
    opencv-python-headless \
    pillow \
    numpy \
    pyyaml \
    matplotlib \
    tqdm

# Create directories
RUN mkdir -p /app/data /app/models /app/runs

# Copy training script
COPY docker_train.py /app/

# Set environment variables to disable MLflow
ENV MLFLOW_TRACKING_URI=""
ENV MLFLOW_DISABLE=1
ENV PYTHONPATH=/app

# Default command
CMD ["python", "docker_train.py"]