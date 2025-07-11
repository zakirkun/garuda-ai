#!/usr/bin/env python3
"""
Garuda AI Assistant Runner
Simple script to run the Streamlit application
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit', 'litellm', 'chromadb', 'langchain', 
        'sentence-transformers', 'PyPDF2', 'python-docx'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_environment():
    """Check environment setup"""
    env_file = Path(".env")
    config_file = Path("config.yaml")
    
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("   Copy .env.example to .env and add your API keys")
        return False
    
    if not config_file.exists():
        print("⚠️  config.yaml file not found")
        return False
    
    print("✅ Environment files found")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["data", "data/vector_store", "data/uploaded_files", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def run_app():
    """Run the Streamlit application"""
    print("🚀 Starting Garuda AI Assistant...")
    print("   Application will be available at: http://localhost:8501")
    print("   Press Ctrl+C to stop the application\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "gui/app.py", 
            "--server.port", "8501",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Garuda AI Assistant stopped")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")

def main():
    """Main function"""
    print("🦅 Garuda AI Assistant")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\n📋 Setup Instructions:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env and add your API keys")
        print("3. Run this script again")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Run application
    run_app()

if __name__ == "__main__":
    main() 