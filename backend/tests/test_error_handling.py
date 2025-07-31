
import pytest
from fastapi.testclient import TestClient
import os
from unittest.mock import patch

# Test edilecek ana uygulamayı ve ayarları import et
from app.main import app
from app.core.config import settings
from app.ai.exceptions import FaceNotFoundError, MultipleFacesError

# Test client'ını oluştur
client = TestClient(app)

# Test varlıklarının bulunduğu klasör
TEST_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "test_assets")
# Proje kök dizini
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

@pytest.fixture(autouse=True)
def override_test_mode():
    """
    Tüm testler için rate limiter'ı devre dışı bırakmak amacıyla
    TEST_MODE'u zorla True yapar.
    """
    original_mode = settings.TEST_MODE
    settings.TEST_MODE = True
    yield
    settings.TEST_MODE = original_mode

# --- Test Senaryoları ---

def test_upload_successful():
    """Başarılı bir fotoğraf yükleme ve işleme senaryosunu test eder."""
    valid_image_path = os.path.join(PROJECT_ROOT, "assets", "test_portrait_face_detected.jpg")
    
    with open(valid_image_path, "rb") as f:
        response = client.post("/api/v1/photos/preview", files={"file": ("test.jpg", f, "image/jpeg")})
    
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/png'

def test_upload_no_face():
    """Yüz algılanmayan bir fotoğraf yüklendiğinde doğru hatayı test eder (mocking ile)."""
    valid_image_path = os.path.join(PROJECT_ROOT, "assets", "test_portrait_face_detected.jpg")

    # process_photo fonksiyonunu FaceNotFoundError fırlatacak şekilde mock'la
    with patch('app.api.v1.endpoints.photos.process_photo', side_effect=FaceNotFoundError) as mock_process:
        with open(valid_image_path, "rb") as f:
            response = client.post("/api/v1/photos/preview", files={"file": ("no_face.jpg", f, "image/jpeg")})
        
        assert mock_process.called
        assert response.status_code == 400
        assert "Please ensure your face is clearly visible" in response.json()["detail"]

def test_upload_multiple_faces():
    """Birden fazla yüz içeren bir fotoğraf yüklendiğinde doğru hatayı test eder (mocking ile)."""
    valid_image_path = os.path.join(PROJECT_ROOT, "assets", "test_portrait_face_detected.jpg")

    # process_photo fonksiyonunu MultipleFacesError fırlatacak şekilde mock'la
    with patch('app.api.v1.endpoints.photos.process_photo', side_effect=MultipleFacesError) as mock_process:
        with open(valid_image_path, "rb") as f:
            response = client.post("/api/v1/photos/preview", files={"file": ("multiple_faces.jpg", f, "image/jpeg")})
    
        assert mock_process.called
        assert response.status_code == 400
        assert "Please use a photo with only one person" in response.json()["detail"]

def test_upload_file_too_large():
    """Çok büyük bir dosya yüklendiğinde doğru hatayı test eder."""
    large_file_path = os.path.join(TEST_ASSETS_DIR, "too_large.jpg")
    
    with open(large_file_path, "rb") as f:
        response = client.post("/api/v1/photos/preview", files={"file": ("large.jpg", f, "image/jpeg")})
        
    assert response.status_code == 413
    assert "File size is too large" in response.json()["detail"]

def test_upload_invalid_file_format():
    """Geçersiz (bozuk) bir görüntü dosyası yüklendiğinde doğru hatayı test eder."""
    invalid_file_path = os.path.join(TEST_ASSETS_DIR, "invalid_file.jpg")
    
    with open(invalid_file_path, "rb") as f:
        response = client.post("/api/v1/photos/preview", files={"file": ("invalid.jpg", f, "image/jpeg")})
        
    assert response.status_code == 400
    assert "Invalid image file. Please upload a valid image." in response.json()["detail"]

def test_upload_unsupported_mime_type():
    """Desteklenmeyen bir dosya türü (MIME type) yüklendiğinde doğru hatayı test eder."""
    valid_image_path = os.path.join(PROJECT_ROOT, "assets", "test_portrait_face_detected.jpg")
    
    with open(valid_image_path, "rb") as f:
        response = client.post("/api/v1/photos/preview", files={"file": ("test.txt", f, "text/plain")})
        
    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["detail"]
