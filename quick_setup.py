#!/usr/bin/env python3
"""
Garuda AI Assistant - Quick Setup Script
Automated setup for first-time installation
"""

import os
import subprocess
import sys
from pathlib import Path
import shutil

def print_header():
    """Print setup header"""
    print("🦅" * 20)
    print("🦅 Garuda AI Assistant - Quick Setup")
    print("🦅" * 20)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version.split()[0]} detected")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = [
        "data",
        "data/vector_store", 
        "data/uploaded_files",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}/")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("   Please run: pip install -r requirements.txt")
        sys.exit(1)

def setup_environment():
    """Setup environment file"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env from template")
        else:
            # Create basic .env file
            env_content = """# API Keys Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Application Settings
APP_NAME=Garuda AI Assistant
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo
MAX_TOKENS=4096
TEMPERATURE=0.7

# Vector Store Settings
VECTOR_STORE_PATH=./data/vector_store
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
"""
            with open(".env", "w") as f:
                f.write(env_content)
            print("✅ Created .env file")
    else:
        print("✅ .env file already exists")

def setup_api_keys():
    """Interactive API key setup"""
    print("\n🔑 API Key Setup")
    print("You can set up API keys now or later by editing the .env file")
    
    setup_keys = input("Do you want to set up API keys now? (y/n): ").lower().strip()
    
    if setup_keys == 'y':
        api_keys = {}
        
        print("\nEnter your API keys (press Enter to skip):")
        
        # OpenAI
        openai_key = input("OpenAI API Key: ").strip()
        if openai_key:
            api_keys["OPENAI_API_KEY"] = openai_key
        
        # Anthropic
        anthropic_key = input("Anthropic API Key: ").strip()
        if anthropic_key:
            api_keys["ANTHROPIC_API_KEY"] = anthropic_key
        
        # Hugging Face
        hf_key = input("Hugging Face API Key: ").strip()
        if hf_key:
            api_keys["HUGGINGFACE_API_KEY"] = hf_key
        
        if api_keys:
            # Update .env file
            with open(".env", "r") as f:
                env_content = f.read()
            
            for key, value in api_keys.items():
                # Replace the placeholder
                env_content = env_content.replace(
                    f"{key}=your_{key.lower().replace('_', '_')}_here",
                    f"{key}={value}"
                )
            
            with open(".env", "w") as f:
                f.write(env_content)
            
            print(f"✅ Updated {len(api_keys)} API keys")
        else:
            print("⚠️  No API keys provided")
    else:
        print("⚠️  Remember to add your API keys to .env file later")

def verify_installation():
    """Verify the installation"""
    print("\n🧪 Verifying installation...")
    
    # Check if all required files exist
    required_files = [
        "requirements.txt",
        "config.yaml", 
        ".env",
        "core/agent.py",
        "gui/app.py"
    ]
    
    all_good = True
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file}")
            all_good = False
    
    if all_good:
        print("✅ Installation verified successfully!")
    else:
        print("❌ Some files are missing")
        return False
    
    # Test import
    try:
        import streamlit
        import litellm
        import chromadb
        print("✅ Core dependencies can be imported")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def show_next_steps():
    """Show next steps to user"""
    print("\n🚀 Setup Complete!")
    print("\nNext steps:")
    print("1. Edit .env file and add your API keys if you haven't already")
    print("2. Run the application:")
    print("   python run.py")
    print("   or")
    print("   streamlit run gui/app.py")
    print("\n3. Open http://localhost:8501 in your browser")
    print("\n4. Upload some documents and start chatting!")
    print("\n📖 For detailed instructions, see README.md")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    install_dependencies()
    
    # Setup environment
    setup_environment()
    
    # Setup API keys
    setup_api_keys()
    
    # Verify installation
    if verify_installation():
        show_next_steps()
    else:
        print("\n❌ Setup completed with errors. Please check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 