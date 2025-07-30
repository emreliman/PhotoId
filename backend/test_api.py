import requests
import os

# API'nin çalıştığı adres
BASE_URL = "http://127.0.0.1:8000"
API_V1_PREFIX = "/api/v1"

# Test edilecek endpoint
PREVIEW_ENDPOINT = f"{BASE_URL}{API_V1_PREFIX}/photos/preview"

# Test için kullanılacak fotoğrafın yolu
# Bu script backend klasöründen çalıştırılacağı için ../ ile üst dizine çıkılır
TEST_IMAGE_PATH = os.path.join("..", "uploads", "test_portrait.jpg")

def test_preview_endpoint():
    """
    /api/v1/photos/preview endpoint'ini test eder.
    """
    print(f"--- Endpoint Testi Başlatılıyor: {PREVIEW_ENDPOINT} ---")

    # Test fotoğrafının var olup olmadığını kontrol et
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"HATA: Test fotoğrafı bulunamadı: {TEST_IMAGE_PATH}")
        return

    print(f"Test fotoğrafı: {TEST_IMAGE_PATH}")

    try:
        # Fotoğrafı binary modda aç ve isteği gönder
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': (os.path.basename(TEST_IMAGE_PATH), f, 'image/jpeg')}
            print("POST isteği gönderiliyor...")
            response = requests.post(PREVIEW_ENDPOINT, files=files)

        # Yanıtı kontrol et
        print(f"Yanıt Status Kodu: {response.status_code}")

        if response.status_code == 200:
            # Başarılı yanıtın içeriğini bir dosyaya yaz
            output_path = os.path.join("..", "assets", "api_test_output.png")
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"BAŞARILI: Yanıt 200 OK. İşlenmiş fotoğraf şuraya kaydedildi: {output_path}")
        else:
            # Hatalı yanıtın detayını yazdır
            print(f"HATA: Beklenmeyen status kodu. Sunucu yanıtı:")
            try:
                print(response.json())
            except requests.exceptions.JSONDecodeError:
                print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"HATA: API isteği sırasında bir hata oluştu: {e}")
        print("Lütfen FastAPI sunucusunun çalıştığından emin olun: `uvicorn app.main:app --reload`")

if __name__ == "__main__":
    test_preview_endpoint()