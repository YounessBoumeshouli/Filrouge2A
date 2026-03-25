#!/usr/bin/env python3
"""
Quick Start Script for YOLO API Server
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("🚀 Starting YOLO API Server...")
    print("=" * 40)
    
    # Check if model exists
    model_path = Path("models/ceramic_yolo_trained.pt")
    if not model_path.exists():
        print("❌ Model not found!")
        print("Run this first: docker cp ceramic-yolo-trainer:/app/models/ceramic_yolo_trained.pt models/ceramic_yolo_trained.pt")
        return
    
    print("✅ Model found")
    print("🌐 Starting server at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    print("-" * 40)
    
    try:
        subprocess.run([sys.executable, "yolo_api.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()