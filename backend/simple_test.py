import requests
import time

def test_api():
    print("🔍 API Test başlatılıyor...")
    
    # Test 1: Ana endpoint
    try:
        response = requests.get("http://localhost:8080/")
        print(f"✅ Ana endpoint: {response.status_code}")
        print(f"📄 Response: {response.json()}")
    except Exception as e:
        print(f"❌ Ana endpoint hatası: {e}")
    
    # Test 2: Health check
    try:
        response = requests.get("http://localhost:8080/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"📄 Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check hatası: {e}")
    
    # Test 3: Swagger docs
    try:
        response = requests.get("http://localhost:8080/docs")
        print(f"✅ Swagger docs: {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger docs hatası: {e}")

if __name__ == "__main__":
    print("🚀 PhotoID AI Backend Test")
    print("=" * 40)
    test_api() 