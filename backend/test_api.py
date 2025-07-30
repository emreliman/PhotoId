import requests
import time

def test_api():
    print("🔍 PhotoID AI API Test başlatılıyor...")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8080"
    
    # Test 1: Ana endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Ana endpoint: {response.status_code}")
        print(f"📄 Response: {response.json()}")
    except Exception as e:
        print(f"❌ Ana endpoint hatası: {e}")
    
    # Test 2: Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"📄 Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check hatası: {e}")
    
    # Test 3: Test endpoint
    try:
        response = requests.get(f"{base_url}/test")
        print(f"✅ Test endpoint: {response.status_code}")
        print(f"📄 Response: {response.json()}")
    except Exception as e:
        print(f"❌ Test endpoint hatası: {e}")
    
    # Test 4: Swagger docs
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"✅ Swagger docs: {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger docs hatası: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test tamamlandı!")

if __name__ == "__main__":
    print("🚀 PhotoID AI Backend Test")
    print("⏳ Server başlatılıyor...")
    time.sleep(3)  # Server'ın başlaması için bekle
    test_api() 