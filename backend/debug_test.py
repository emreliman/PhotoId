import requests
import time

def test_connection():
    print("🔍 Bağlantı testi başlatılıyor...")
    
    # Test 1: Basit HTTP isteği
    try:
        print("📡 HTTP isteği gönderiliyor...")
        response = requests.get("http://127.0.0.1:8080/", timeout=5)
        print(f"✅ Başarılı! Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Bağlantı hatası: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout hatası: {e}")
    except Exception as e:
        print(f"❌ Genel hata: {e}")
    
    # Test 2: Port kontrolü
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8080))
        if result == 0:
            print("✅ Port 8080 açık")
        else:
            print("❌ Port 8080 kapalı")
        sock.close()
    except Exception as e:
        print(f"❌ Port test hatası: {e}")

if __name__ == "__main__":
    print("🚀 Debug Test")
    print("=" * 30)
    test_connection() 