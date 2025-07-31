from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Request
from fastapi.responses import FileResponse
import shutil
import os
import uuid
import imghdr
from typing import Optional
from io import BytesIO
import logging

# AI pipeline, custom exceptions, and preset sizes
from app.ai.processing import process_photo, PRESET_SIZES
from app.ai.exceptions import PhotoProcessingError, FaceNotFoundError, MultipleFacesError, ImageReadError

# Logger setup
logger = logging.getLogger(__name__)

router = APIRouter()

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
ALLOWED_FORMATS = {"jpeg", "jpg", "png"}
ALLOWED_MIME_TYPES = {
    "image/jpeg": {"jpeg", "jpg"},
    "image/png": {"png"}
}

# Temporary file storage
TEMP_DIR = os.path.join("uploads", "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

def validate_image_file(file: UploadFile) -> None:
    """
    Validates the uploaded file and performs security checks.
    Raises HTTPException on error.
    """
    # 1. File size check
    contents = file.file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size is too large. Maximum size: {MAX_FILE_SIZE/1024/1024:.1f}MB"
        )
    
    # Reset file pointer after reading
    file.file.seek(0)
    
    # 2. MIME type check
    content_type = file.content_type
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type. Allowed formats: {', '.join(ALLOWED_FORMATS)}"
        )
    
    # 3. File content check (magic number)
    img_format = imghdr.what(None, h=contents)
    if img_format not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file. Please upload a valid image."
        )
    
    # 4. MIME type vs. actual format check
    if img_format not in ALLOWED_MIME_TYPES[content_type]:
        raise HTTPException(
            status_code=400,
            detail="File format and content type mismatch."
        )

@router.post("/preview",
    responses={
        200: {"content": {"image/png": {}}},
        400: {"description": "Invalid image, parameters, or processing error (e.g., no face found)."},
        413: {"description": "File too large (max 10MB)."},
        415: {"description": "Unsupported file type."},
        500: {"description": "Internal server error."}
    },
    summary="Process a Photo with Dynamic Sizing",
    description="Upload a photo and process it. Specify a preset format or custom dimensions. Supports JPG and PNG formats up to 10MB."
)
async def preview_photo(
    request: Request,
    file: UploadFile = File(...),
    output_format: Optional[str] = Query("passport_eu", enum=list(PRESET_SIZES.keys())),
    custom_width: Optional[int] = Query(None, gt=0, le=2000),
    custom_height: Optional[int] = Query(None, gt=0, le=2000)
):
    """
    Processes a photo according to the specified format or custom size.
    - **file**: Photo to upload (JPG/PNG, max 10MB).
    - **output_format**: A key from `PRESET_SIZES` (e.g., "passport_tr").
    - **custom_width**: Custom width in pixels.
    - **custom_height**: Custom height in pixels.
    """
    client_ip = request.client.host
    logger.info(f"Request received from IP: {client_ip} for file: {file.filename}")

    validate_image_file(file)
    
    output_size = None
    if output_format == 'custom' and custom_width and custom_height:
        output_size = (custom_width, custom_height)
    elif output_format in PRESET_SIZES:
        output_size = PRESET_SIZES[output_format]
    
    if not output_size:
        raise HTTPException(status_code=400, detail="You must provide a valid output_format or custom dimensions.")

    temp_id = str(uuid.uuid4())
    input_path = os.path.join(TEMP_DIR, f"{temp_id}_{file.filename}")
    processed_output_path = os.path.join(TEMP_DIR, f"{temp_id}_processed.png")

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Starting photo processing for {input_path}")
        processed_image = process_photo(input_image_path=input_path, output_size=output_size)
        processed_image.save(processed_output_path, 'PNG')

        return FileResponse(
            processed_output_path,
            media_type="image/png",
            filename=f"processed_{output_format}.png"
        )

    except FaceNotFoundError as e:
        logger.warning(f"Face not found for {input_path}. Error: {e}")
        raise HTTPException(status_code=400, detail="Please ensure your face is clearly visible in the photo.")
    except MultipleFacesError as e:
        logger.warning(f"Multiple faces detected for {input_path}. Error: {e}")
        raise HTTPException(status_code=400, detail="Please use a photo with only one person.")
    except ImageReadError as e:
        logger.error(f"Cannot read image file {input_path}. Error: {e}")
        raise HTTPException(status_code=400, detail="The uploaded image file is corrupted or invalid.")
    except PhotoProcessingError as e:
        logger.error(f"An unexpected processing error occurred for {input_path}. Error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during photo processing.")
    except Exception as e:
        logger.exception(f"A critical server error occurred for {input_path}. Error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred.")
    finally:
        # Clean up the original uploaded file
        if os.path.exists(input_path):
            os.remove(input_path)
