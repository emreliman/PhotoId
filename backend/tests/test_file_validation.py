import pytest
from fastapi.testclient import TestClient
import os
import shutil
from pathlib import Path

# Test modu aktif
os.environ["TEST_MODE"] = "true"

# Test modu aktifken app'i import et
from app.main import app
client = TestClient(app)

# Test dosyalarının bulunduğu klasör
TEST_FILES_DIR = Path(__file__).parent / "test_assets"
os.makedirs(TEST_FILES_DIR, exist_ok=True)

def setup_module(module):
    """Test başlamadan önce gerekli test dosyalarını kopyala"""
    source_dir = Path(__file__).parent.parent.parent / "assets"
    
    # Test için gerekli dosyaları kopyala
    source = source_dir / "test_portrait_face_detected.jpg"
    if source.exists():
        shutil.copy2(source, TEST_FILES_DIR / "test_portrait.jpg")

def teardown_module(module):
    """Test bitiminde geçici dosyaları temizle"""
    if TEST_FILES_DIR.exists():
        for file in TEST_FILES_DIR.iterdir():
            if file.is_file():
                file.unlink()

def test_valid_jpg_upload():
    """Geçerli bir JPG dosyası yükleme testi"""
    file_path = TEST_FILES_DIR / "test_portrait.jpg"
    
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/v1/photos/preview",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

# TODO: PNG testi için yüz içeren uygun bir PNG dosyası eklendiğinde test_valid_png_upload() eklenecek

def test_large_file():
    """10MB'dan büyük dosya yükleme testi"""
    # 11MB'lık boş bir dosya oluştur
    large_file_path = TEST_FILES_DIR / "temp_large.jpg"
    with open(large_file_path, "wb") as f:
        f.seek(11 * 1024 * 1024 - 1)  # 11MB
        f.write(b"\0")
    
    try:
        with open(large_file_path, "rb") as f:
            response = client.post(
                "/api/v1/photos/preview",
                files={"file": ("large.jpg", f, "image/jpeg")}
            )
        
        assert response.status_code == 400
        assert "Dosya boyutu çok büyük" in response.json()["detail"]
    
    finally:
        # Geçici dosyayı temizle
        if os.path.exists(large_file_path):
            os.remove(large_file_path)

def test_wrong_mime_type():
    """Yanlış MIME type ile dosya yükleme testi"""
    file_path = TEST_FILES_DIR / "test_portrait.jpg"
    
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/v1/photos/preview",
            files={"file": ("test.jpg", f, "image/gif")}  # Yanlış MIME type
        )
    
    assert response.status_code == 400
    assert "Desteklenmeyen dosya türü" in response.json()["detail"]

def test_unsupported_format():
    """Desteklenmeyen format (gif) yükleme testi"""
    # Test için geçici bir GIF dosyası oluştur
    gif_file_path = TEST_FILES_DIR / "temp_test.gif"
    with open(gif_file_path, "wb") as f:
        # Minimal GIF dosya başlığı
        f.write(b"GIF89a\x01\x00\x01\x00\x00\x00\x00;")
    
    try:
        with open(gif_file_path, "rb") as f:
            response = client.post(
                "/api/v1/photos/preview",
                files={"file": ("test.gif", f, "image/gif")}
            )
        
        assert response.status_code == 400
        assert "Desteklenmeyen dosya türü" in response.json()["detail"]
    
    finally:
        # Geçici dosyayı temizle
        if os.path.exists(gif_file_path):
            os.remove(gif_file_path)

def test_format_mime_type_mismatch():
    """Dosya formatı ve MIME type uyumsuzluğu testi"""
    file_path = TEST_FILES_DIR / "test_portrait.jpg"
    
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/v1/photos/preview",
            files={"file": ("test.jpg", f, "image/png")}  # JPG dosyası için PNG MIME type
        )
    
    assert response.status_code == 400
    assert "Dosya formatı ve içerik türü uyumsuz" in response.json()["detail"]
