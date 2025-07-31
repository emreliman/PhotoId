from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
import shutil
import os
import uuid
import imghdr
from typing import Optional
from io import BytesIO

# AI pipeline ve preset boyutları import et
from app.ai.processing import process_photo, PRESET_SIZES

router = APIRouter()

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
ALLOWED_FORMATS = {"jpeg", "jpg", "png"}
ALLOWED_MIME_TYPES = {
    "image/jpeg": {"jpeg", "jpg"},
    "image/png": {"png"}
}

# Geçici dosyaların saklanacağı klasör
TEMP_DIR = os.path.join("uploads", "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

def validate_image_file(file: UploadFile) -> None:
    """
    Yüklenen dosyayı validate eder ve güvenlik kontrollerini yapar.
    Hata durumunda HTTPException fırlatır.
    """
    # 1. Dosya boyutu kontrolü
    file_size = 0
    contents = BytesIO()
    
    # Dosyayı memory'de oku ve boyutunu kontrol et
    for chunk in file.file:
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Dosya boyutu çok büyük. Maksimum boyut: {MAX_FILE_SIZE/1024/1024:.1f}MB"
            )
        contents.write(chunk)
    
    # Dosya pointer'ını başa al
    file.file.seek(0)
    contents.seek(0)
    
    # 2. MIME type kontrolü
    content_type = file.content_type
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Desteklenmeyen dosya türü. İzin verilen formatlar: {', '.join(ALLOWED_FORMATS)}"
        )
    
    # 3. Dosya içerik kontrolü
    img_format = imghdr.what(None, h=contents.read())
    if img_format not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail="Geçersiz görüntü dosyası. Lütfen geçerli bir resim dosyası yükleyin."
        )
    
    # 4. MIME type ile gerçek format eşleşmesi
    if img_format not in ALLOWED_MIME_TYPES[content_type]:
        raise HTTPException(
            status_code=400,
            detail="Dosya formatı ve içerik türü uyumsuz."
        )
    
    # Dosya pointer'ını tekrar başa al
    file.file.seek(0)

@router.post("/preview",
    responses={
        200: {"content": {"image/png": {}}},
        400: {"description": "Invalid image or parameters."},
        413: {"description": "File too large (max 10MB)."},
        415: {"description": "Unsupported file type."},
        500: {"description": "Internal server error."}
    },
    summary="Process a Photo with Dynamic Sizing",
    description="Upload a photo and process it. Specify a preset format or custom dimensions. Supports JPG and PNG formats up to 10MB."
)
async def preview_photo(
    file: UploadFile = File(...),
    output_format: Optional[str] = Query("passport_eu", enum=list(PRESET_SIZES.keys())),
    custom_width: Optional[int] = Query(None, gt=0, le=2000),
    custom_height: Optional[int] = Query(None, gt=0, le=2000)
):
    """
    Bir fotoğrafı işler ve belirtilen formata veya özel boyuta göre ayarlar.
    - **file**: Yüklenecek fotoğraf (JPG/PNG, max 10MB).
    - **output_format**: `PRESET_SIZES` içinden bir anahtar (örn: "passport_tr").
    - **custom_width**: Özel genişlik (piksel).
    - **custom_height**: Özel yükseklik (piksel).
    """
    # Dosya validasyonu
    validate_image_file(file)
    output_size = None
    if custom_width and custom_height:
        output_size = (custom_width, custom_height)
    elif output_format and output_format in PRESET_SIZES:
        output_size = PRESET_SIZES[output_format]
    
    if not output_size:
        raise HTTPException(status_code=400, detail="Geçerli bir çıktı formatı veya özel boyut belirtmelisiniz.")

    temp_id = str(uuid.uuid4())
    input_path = os.path.join(TEMP_DIR, f"{temp_id}_{file.filename}")
    processed_output_path = os.path.join(TEMP_DIR, f"{temp_id}_processed.png")

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        processed_image = process_photo(input_image_path=input_path, output_size=output_size)

        if processed_image is None:
            raise HTTPException(
                status_code=400,
                detail="Fotoğraf işlenemedi. Kalite kontrolünü geçemedi veya yüz algılanamadı."
            )

        processed_image.save(processed_output_path, 'PNG')

        return FileResponse(
            processed_output_path,
            media_type="image/png",
            filename=f"processed_{output_format}.png"
        )

    except Exception as e:
        print(f"Sunucu Hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {e}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
