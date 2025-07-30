#!/usr/bin/env python3
"""
PhotoID AI Server Başlatma Script'i
"""

import subprocess
import sys
import time
import requests

def start_server():
    print("🚀 PhotoID AI Server başlatılıyor...")
    print("📡 URL: http://127.0.0.1:8080")
    print("📚 Docs: http://127.0.0.1:8080/docs")
    print("=" * 50)
    
    # Server'ı başlat
    try:
        process = subprocess.Popen([
            sys.executable, "-c", 
            "from app.main_simple import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8080)"
        ])
        
        print(f"✅ Server başlatıldı (PID: {process.pid})")
        
        # Server'ın başlaması için bekle
        time.sleep(3)
        
        # Test et
        test_server()
        
        # Server'ı çalışır durumda tut
        process.wait()
        
    except Exception as e:
        print(f"❌ Server başlatma hatası: {e}")

def test_server():
    print("\n🔍 Server test ediliyor...")
    
    try:
        response = requests.get("http://127.0.0.1:8080/", timeout=5)
        print(f"✅ Ana endpoint: {response.status_code}")
        print(f"📄 Response: {response.json()}")
        
        response = requests.get("http://127.0.0.1:8080/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        print(f"📄 Response: {response.json()}")
        
        response = requests.get("http://127.0.0.1:8080/test", timeout=5)
        print(f"✅ Test endpoint: {response.status_code}")
        print(f"📄 Response: {response.json()}")
        
        print("\n🎉 Server başarıyla çalışıyor!")
        print("🌐 Tarayıcıda http://127.0.0.1:8080/docs adresini açabilirsiniz")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")

if __name__ == "__main__":
    start_server() 