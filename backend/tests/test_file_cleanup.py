
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, ANY
import os

# Test edilecek ana uygulamayı ve ayarları import et
from app.main import app
from app.core.config import settings

# Test client'ını oluştur
client = TestClient(app)

# Proje kök dizini
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

@pytest.fixture(autouse=True)
def override_test_mode():
    """Rate limiter'ı devre dışı bırakmak için TEST_MODE'u zorla True yapar."""
    original_mode = settings.TEST_MODE
    settings.TEST_MODE = True
    yield
    settings.TEST_MODE = original_mode

@patch('app.api.v1.endpoints.photos.uuid.uuid4')
@patch('app.api.v1.endpoints.photos.cleanup_file')
def test_cleanup_on_success(mock_cleanup_file, mock_uuid):
    """Başarılı bir istekten sonra dosyaların temizlendiğini doğrular."""
    # Mock UUID'yi ayarla
    mock_uuid.return_value = 'test-uuid'
    
    # Geçerli bir resim dosyası kullan
    valid_image_path = os.path.join(PROJECT_ROOT, "assets", "test_portrait_face_detected.jpg")
    test_filename = "test_image.jpg"

    # Beklenen dosya yollarını oluştur
    expected_input_path = os.path.join("uploads", "temp", f"test-uuid_{test_filename}")
    expected_output_path = os.path.join("uploads", "temp", "test-uuid_processed.png")

    with open(valid_image_path, "rb") as f:
        response = client.post(
            "/api/v1/photos/preview", 
            files={"file": (test_filename, f, "image/jpeg")}
        )

    # API'nin başarılı olduğunu doğrula
    assert response.status_code == 200

    # cleanup_file fonksiyonunun doğru dosyalar için çağrıldığını doğrula
    # ANY, BackgroundTasks nesnesini temsil eder, çünkü ona doğrudan erişimimiz yok
    mock_cleanup_file.assert_any_call(expected_input_path)
    # Arka plan görevi olarak eklendiği için, doğrudan çağrıyı değil, 
    # add_task ile eklendiğini kontrol etmek daha doğru olur.
    # Ancak bu basit test için any_call yeterlidir.
    mock_cleanup_file.assert_any_call(expected_output_path)
