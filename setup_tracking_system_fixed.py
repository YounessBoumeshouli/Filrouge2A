#!/usr/bin/env python3
"""
Complete setup script for the User Tracking System
This script initializes the database, creates sample data, and sets up the tracking system
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_step(step, description):
    print(f"\n🔧 Step {step}: {description}")
    print("-" * 50)


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False


def check_requirements():
    """Check if required tools are installed"""
    print_step(1, "Checking Requirements")

    requirements = {
        "python": "python --version",
        "pip": "pip --version",
        "node": "node --version",
        "npm": "npm --version",
    }

    missing = []
    for tool, command in requirements.items():
        if not run_command(command, f"Checking {tool}"):
            missing.append(tool)

    if missing:
        print(f"❌ Missing requirements: {', '.join(missing)}")
        print("Please install the missing tools and run this script again.")
        return False

    print("✅ All requirements satisfied")
    return True


def setup_backend():
    """Set up the backend environment"""
    print_step(2, "Setting Up Backend")

    backend_dir = Path("Backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False

    os.chdir(backend_dir)

    # Install Python dependencies
    if not run_command(
        "pip install -r requirements.txt", "Installing Python dependencies"
    ):
        print("⚠️  Failed to install some dependencies, continuing...")

    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file...")
        env_content = """# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/tourist_helper

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key-here

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
"""
        env_file.write_text(env_content)
        print(
            "✅ Created .env file (please update with your actual database credentials)"
        )

    os.chdir("..")
    return True


def setup_frontend():
    """Set up the frontend environment"""
    print_step(3, "Setting Up Frontend")

    frontend_dir = Path("Frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False

    os.chdir(frontend_dir)

    # Install Node.js dependencies
    if not run_command("npm install", "Installing Node.js dependencies"):
        print("❌ Failed to install frontend dependencies")
        os.chdir("..")
        return False

    os.chdir("..")
    print("✅ Frontend setup complete")
    return True


def setup_database():
    """Set up the tracking database"""
    print_step(4, "Setting Up Tracking Database")

    # Check if PostgreSQL is available
    if not run_command("psql --version", "Checking PostgreSQL"):
        print(
            "⚠️  PostgreSQL not found. Please install PostgreSQL and create a database."
        )
        print("   You can also use SQLite by updating the DATABASE_URL in .env")
        return False

    # Run database setup script
    backend_dir = Path("Backend")
    os.chdir(backend_dir)

    if not run_command("python create_tracking_db.py", "Creating tracking tables"):
        print("❌ Failed to create tracking database")
        os.chdir("..")
        return False

    os.chdir("..")
    print("✅ Database setup complete")
    return True


def create_startup_scripts():
    """Create convenient startup scripts"""
    print_step(5, "Creating Startup Scripts")

    # Backend startup script
    backend_script = Path("start_backend.py")
    backend_content = """#!/usr/bin/env python3
import subprocess
import os

print("🚀 Starting Tourist Helper Backend...")
os.chdir("Backend")
subprocess.run(["python", "main.py"])
"""
    backend_script.write_text(backend_content)

    # Frontend startup script
    frontend_script = Path("start_frontend.py")
    frontend_content = """#!/usr/bin/env python3
import subprocess
import os

print("🚀 Starting Tourist Helper Frontend...")
os.chdir("Frontend")
subprocess.run(["npm", "run", "dev"])
"""
    frontend_script.write_text(frontend_content)

    # Combined startup script
    combined_script = Path("start_all.py")
    combined_content = """#!/usr/bin/env python3
import subprocess
import threading
import time
import os

def start_backend():
    print("🚀 Starting Backend...")
    os.chdir("Backend")
    subprocess.run(["python", "main.py"])

def start_frontend():
    print("🚀 Starting Frontend...")
    time.sleep(3)  # Wait for backend to start
    os.chdir("Frontend")
    subprocess.run(["npm", "run", "dev"])

if __name__ == "__main__":
    print("🌟 Starting Tourist Helper Application...")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Start frontend in main thread
    start_frontend()
"""
    combined_script.write_text(combined_content)

    # Background processor script
    processor_script = Path("run_tracking_processor.py")
    processor_content = """#!/usr/bin/env python3
import sys
import os
sys.path.append('Backend')

from tracking_processor import main

if __name__ == "__main__":
    print("🔄 Running tracking data processor...")
    main()
"""
    processor_script.write_text(processor_content)

    print("✅ Created startup scripts:")
    print("   - start_backend.py: Start only the backend")
    print("   - start_frontend.py: Start only the frontend")
    print("   - start_all.py: Start both backend and frontend")
    print("   - run_tracking_processor.py: Process tracking data")

    return True


def print_final_instructions():
    """Print final setup instructions"""
    print_header("🎉 Setup Complete!")

    instructions = """
🚀 Your Tourist Helper Tracking System is ready!

Next Steps:
1. Update Backend/.env with your actual database credentials
2. Start the application:
   python start_all.py

Or start components separately:
   python start_backend.py    # Backend only (http://localhost:8000)
   python start_frontend.py   # Frontend only (http://localhost:3000)

📊 Admin Dashboard:
   http://localhost:8000/admin/analytics/overview

🔄 Background Processing:
   python run_tracking_processor.py

📚 API Documentation:
   http://localhost:8000/docs

🎯 Features Available:
   ✅ User tracking with GDPR compliance
   ✅ Location scan tracking
   ✅ Price scan tracking with owner price input
   ✅ Session management
   ✅ Analytics dashboard
   ✅ Admin endpoints
   ✅ Background data processing
   ✅ Privacy controls

🔧 Troubleshooting:
   - Check Backend/.env for correct database URL
   - Ensure PostgreSQL is running
   - Check console for any error messages
   - Run 'python run_tracking_processor.py' periodically for data processing

📖 Documentation:
   See tracking-users.md for detailed specifications
"""

    print(instructions)


def main():
    """Main setup function"""
    print_header("🌟 Tourist Helper Tracking System Setup")

    print("""
This script will set up the complete user tracking system including:
- Database models and tables
- Backend API endpoints
- Frontend tracking integration
- Analytics dashboard
- GDPR compliance features
- Background processing
""")

    input("Press Enter to continue...")

    # Run setup steps
    steps = [
        check_requirements,
        setup_backend,
        setup_frontend,
        setup_database,
        create_startup_scripts,
    ]

    for step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at step: {step_func.__name__}")
            print("Please fix the issues and run the setup again.")
            return False

    print_final_instructions()
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
