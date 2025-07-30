from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
import shutil
import os
import uuid
from typing import Optional

# AI pipeline ve preset boyutları import et
from app.ai.processing import process_photo, PRESET_SIZES

router = APIRouter()

# Geçici dosyaların saklanacağı klasör
TEMP_DIR = os.path.join("uploads", "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/preview",
    responses={
        200: {"content": {"image/png": {}}},
        400: {"description": "Invalid image or parameters."},
        500: {"description": "Internal server error."}
    },
    summary="Process a Photo with Dynamic Sizing",
    description="Upload a photo and process it. Specify a preset format or custom dimensions."
)
async def preview_photo(
    file: UploadFile = File(...),
    output_format: Optional[str] = Query("passport_eu", enum=list(PRESET_SIZES.keys())),
    custom_width: Optional[int] = Query(None, gt=0, le=2000),
    custom_height: Optional[int] = Query(None, gt=0, le=2000)
):
    """
    Bir fotoğrafı işler ve belirtilen formata veya özel boyuta göre ayarlar.
    - **file**: Yüklenecek fotoğraf.
    - **output_format**: `PRESET_SIZES` içinden bir anahtar (örn: "passport_tr").
    - **custom_width**: Özel genişlik (piksel).
    - **custom_height**: Özel yükseklik (piksel).
    """
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
