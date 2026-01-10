#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime

def create_env_file():
    """Create or update .env file"""
    env_content = """# MongoDB Configuration
# Paste your MongoDB connection string
# Example: mongodb+srv://username:password@cluster.mongodb.net/
MONGO_URI=mongodb+srv://yashdhadgecomp23_db_user:O0sXwd5URoPQBe4s@cluster0.ju2ymsc.mongodb.net/

# Gemini AI Configuration
# Get API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=AIzaSyCoNiRh7_RBktG3TLdOWbvq4MJ9zSSNJ1o

# Application Configuration
DEBUG=True
PORT=5000
"""
    
    if os.path.exists('.env'):
        print("📝 .env file already exists")
        with open('.env', 'r') as f:
            existing = f.read()
        
        # Check if we need to update
        if 'MONGO_URI=' not in existing or 'GEMINI_API_KEY=' not in existing:
            print("⚠️  .env file missing required values. Creating backup...")
            backup_name = f".env.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename('.env', backup_name)
            print(f"✅ Created backup: {backup_name}")
            
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ Updated .env file with required values")
    else:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")

def check_dependencies():
    """Check and install required packages"""
    required = ['flask', 'pymongo', 'google-generativeai', 'python-dotenv', 'flask-cors']
    
    print("🔍 Checking dependencies...")
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✅ All dependencies installed")

def main():
    print("🤖 Agentic Chatbot Setup")
    print("=" * 50)
    
    create_env_file()
    check_dependencies()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nTo start the chatbot, run:")
    print("  python app.py")
    print("\nThen open your browser to: http://localhost:5000")

if __name__ == '__main__':
    main()