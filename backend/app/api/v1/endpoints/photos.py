from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
import uuid

# AI pipeline'ı import et
from app.ai.processing import process_photo

router = APIRouter()

# Geçici dosyaların saklanacağı klasör
TEMP_DIR = os.path.join("uploads", "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/preview",
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Successfully processed image."
        },
        400: {"description": "Invalid image, e.g., no face detected, multiple faces, or poor quality."},
        500: {"description": "Internal server error during processing."}
    },
    summary="Process a Photo for Preview",
    description="Upload a photo to detect a face, perform quality checks, remove the background, and resize it. Returns the processed image."
)
async def preview_photo(file: UploadFile = File(...) ):
    """
    Bir fotoğraf yükler, AI pipeline'dan geçirir ve işlenmiş sonucu döndürür.
    
    - **file**: Yüklenecek fotoğraf dosyası (örn: .jpg, .png).
    """
    # Geçici bir dosya adı oluştur
    temp_id = str(uuid.uuid4())
    input_path = os.path.join(TEMP_DIR, f"{temp_id}_{file.filename}")
    processed_output_path = os.path.join(TEMP_DIR, f"{temp_id}_processed.png")

    try:
        # Yüklenen dosyayı geçici olarak diske yaz
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # AI pipeline'ı çalıştır
        processed_image = process_photo(input_image_path=input_path)

        if processed_image is None:
            # process_photo fonksiyonu kalite kontrolleri başarısız olduğunda None döner
            raise HTTPException(
                status_code=400,
                detail="Fotoğraf işlenemedi. Lütfen tek bir yüz içeren, yüzün net ve tam göründüğü, kenarlara çok yakın olmadığı bir fotoğraf yükleyin."
            )

        # İşlenmiş görüntüyü geçici olarak diske kaydet
        processed_image.save(processed_output_path, 'PNG')

        # Sonucu dosya olarak döndür
        return FileResponse(
            processed_output_path,
            media_type="image/png",
            filename="processed_photo.png"
        )

    except Exception as e:
        # Beklenmedik hataları yakala
        print(f"Sunucu Hatası: {e}")
        raise HTTPException(status_code=500, detail="Fotoğraf işlenirken bir sunucu hatası oluştu.")
    finally:
        # Geçici dosyaları temizle
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(processed_output_path):
            # FileResponse'un dosyayı göndermesi için küçük bir gecikme gerekebilir
            # Bu, daha sağlam bir çözüm için bir arka plan göreviyle yapılmalıdır.
            pass # Şimdilik dosyayı silmiyoruz ki indirilebilsin.