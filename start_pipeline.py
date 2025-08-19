#!/usr/bin/env python3
"""
Startup script for Nyantar AI Pipeline
This script helps you start both the backend and frontend servers
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_frontend():
    """Check if frontend is running"""
    try:
        response = requests.get("http://localhost:3000", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start the backend server"""
    print("🚀 Starting Backend API Server...")
    try:
        # Start backend in background
        subprocess.Popen([sys.executable, "api_server.py"], 
                        cwd=os.getcwd(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
        
        # Wait for backend to start
        print("⏳ Waiting for backend to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_backend():
                print("✅ Backend API Server is running on http://localhost:8000")
                return True
            time.sleep(1)
        
        print("❌ Backend failed to start")
        return False
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

def start_frontend():
    """Start the frontend server"""
    print("🚀 Starting Frontend Server...")
    try:
        # Navigate to frontend directory
        frontend_dir = Path("nyayantar-ui")
        if not frontend_dir.exists():
            print("❌ Frontend directory not found")
            return False
        
        # Start frontend in background
        subprocess.Popen(["npm", "run", "dev"], 
                        cwd=frontend_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
        
        # Wait for frontend to start
        print("⏳ Waiting for frontend to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_frontend():
                print("✅ Frontend Server is running on http://localhost:3000")
                return True
            time.sleep(1)
        
        print("❌ Frontend failed to start")
        return False
        
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return False

def main():
    """Main function"""
    print("🧪 Nyantar AI Pipeline Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("api_server.py").exists():
        print("❌ Please run this script from the RAG-based-Legal-Assistant directory")
        return
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("❌ Backend dependencies not installed. Please run:")
        print("   pip install -r requirements.txt")
        return
    
    # Start backend
    backend_ok = start_backend()
    
    # Start frontend
    frontend_ok = start_frontend()
    
    print("\n" + "=" * 50)
    print("📊 Startup Results:")
    print(f"Backend: {'✅ RUNNING' if backend_ok else '❌ FAILED'}")
    print(f"Frontend: {'✅ RUNNING' if frontend_ok else '❌ FAILED'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 Pipeline is ready!")
        print("\n🌐 Access your application:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        
        print("\n💡 Usage:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Type a legal question or click a quick start button")
        print("   3. You'll be redirected to the chat page")
        print("   4. The chatbot will respond using the RAG system")
        
        print("\n⚠️  To stop the servers:")
        print("   Press Ctrl+C in each terminal window")
        
    else:
        print("\n⚠️  Some services failed to start.")
        if not backend_ok:
            print("\nTo start backend manually:")
            print("   python api_server.py")
        if not frontend_ok:
            print("\nTo start frontend manually:")
            print("   cd nyayantar-ui")
            print("   npm run dev")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        print("Please stop the servers manually if needed.")
