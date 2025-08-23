#!/usr/bin/env python3
"""
Setup script for Ollama and the required model.
This script helps users install Ollama and pull the llama3.2:3b model.
"""

import subprocess
import sys
import os
import platform
import requests
import time

def check_ollama_installed():
    """Check if Ollama is already installed and running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is already running!")
            return True
    except:
        pass
    
    # Check if ollama command exists
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed but not running.")
            print("   Please start Ollama with: ollama serve")
            return False
    except FileNotFoundError:
        pass
    
    return False

def install_ollama():
    """Install Ollama based on the operating system."""
    system = platform.system().lower()
    
    print(f"🔧 Installing Ollama for {system}...")
    
    if system == "darwin":  # macOS
        print("📥 Downloading Ollama for macOS...")
        subprocess.run([
            "curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"
        ], shell=True)
        
    elif system == "linux":
        print("📥 Downloading Ollama for Linux...")
        subprocess.run([
            "curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"
        ], shell=True)
        
    elif system == "windows":
        print("📥 Please download Ollama for Windows from: https://ollama.ai/download")
        print("   After installation, restart your terminal and run this script again.")
        return False
        
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False
    
    print("✅ Ollama installation completed!")
    return True

def start_ollama():
    """Start the Ollama service."""
    print("🚀 Starting Ollama service...")
    
    # Start ollama serve in the background
    try:
        subprocess.Popen(["ollama", "serve"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for service to start
        print("⏳ Waiting for Ollama service to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    print("✅ Ollama service is now running!")
                    return True
            except:
                pass
            time.sleep(1)
            if i % 5 == 0:
                print(f"   Still waiting... ({i+1}/30 seconds)")
        
        print("❌ Ollama service failed to start within 30 seconds.")
        return False
        
    except Exception as e:
        print(f"❌ Failed to start Ollama: {e}")
        return False

def pull_model():
    """Pull the required llama3.2:3b model."""
    print("📥 Pulling llama3.2:3b model...")
    print("   This may take several minutes depending on your internet connection...")
    
    try:
        result = subprocess.run(
            ["ollama", "pull", "llama3.2:3b"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Model pulled successfully!")
            return True
        else:
            print(f"❌ Failed to pull model: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error pulling model: {e}")
        return False

def verify_setup():
    """Verify that everything is working correctly."""
    print("🔍 Verifying setup...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
            
            if "llama3.2:3b" in model_names:
                print("✅ Setup verification successful!")
                print("🎉 You're ready to run the Style Finder application!")
                return True
            else:
                print("❌ Model not found. Please run the setup again.")
                return False
        else:
            print("❌ Cannot connect to Ollama service.")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Style Finder - Ollama Setup")
    print("=" * 40)
    
    # Check if Ollama is already running
    if check_ollama_installed():
        # Check if model is available
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                
                if "llama3.2:3b" in model_names:
                    print("✅ Model llama3.2:3b is already available!")
                    print("🎉 Setup is complete!")
                    return
                else:
                    print("📥 Model not found, pulling now...")
                    if pull_model():
                        print("🎉 Setup is complete!")
                        return
                    else:
                        print("❌ Failed to pull model.")
                        return
        except:
            pass
    
    # Install Ollama if needed
    if not check_ollama_installed():
        if not install_ollama():
            print("❌ Installation failed. Please try again.")
            return
    
    # Start Ollama service
    if not start_ollama():
        print("❌ Failed to start Ollama service.")
        return
    
    # Pull the required model
    if not pull_model():
        print("❌ Failed to pull model.")
        return
    
    # Verify setup
    if verify_setup():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Run the Style Finder app: python app.py")
    else:
        print("\n❌ Setup verification failed.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
