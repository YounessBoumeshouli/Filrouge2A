#!/usr/bin/env python3
"""
Simple startup script for RAG API without reload
"""

import os
import sys
import subprocess
import socket


def is_port_available(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", port))
            return True
    except OSError:
        return False


def find_available_port(start_port=8002):
    """Find an available port"""
    for port in range(start_port, start_port + 10):
        if is_port_available(port):
            return port
    return None


def main():
    print("=== RAG API Startup (Simple) ===")
    print("Make sure Ollama is running: ollama serve")
    print("Make sure model is downloaded: ollama pull gemma2:2b")
    print()

    # Find available port
    port = 8002  # Start with 8002 instead of 8001
    if not is_port_available(port):
        print(f"Port {port} is in use, finding alternative...")
        port = find_available_port(8002)
        if not port:
            print("❌ No available ports found")
            input("Press Enter to exit...")
            return

    print(f"Using port: {port}")

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(script_dir, "backend")

    # Add backend to Python path
    sys.path.insert(0, backend_dir)

    # Change to backend directory
    os.chdir(backend_dir)

    print(f"Working directory: {os.getcwd()}")

    try:
        # Install dependencies if needed
        try:
            from app.main_keras_free import app
        except ImportError:
            print("Installing dependencies...")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    "requirements_keras_free.txt",
                ]
            )
            from app.main_keras_free import app

        # Start server without reload to avoid warnings
        print(f"Starting RAG API server on http://localhost:{port}")
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=port)

    except Exception as e:
        print(f"Error starting server: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
