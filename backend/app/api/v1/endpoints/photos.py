from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Request, BackgroundTasks
from fastapi.responses import FileResponse
import shutil
import os
import uuid
import imghdr
import logging
import time
import random
from typing import Optional

# AI pipeline, custom exceptions, and preset sizes
from app.ai.processing import process_photo, PRESET_SIZES
from app.ai.exceptions import PhotoProcessingError, FaceNotFoundError, MultipleFacesError, ImageReadError

# Logger setup
logger = logging.getLogger(__name__)

router = APIRouter()

# --- Constants ---
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FORMATS = {"jpeg", "jpg", "png"}
ALLOWED_MIME_TYPES = {
    "image/jpeg": {"jpeg", "jpg"},
    "image/png": {"png"}
}
TEMP_DIR = os.path.join("uploads", "temp")
CLEANUP_MAX_AGE_SECONDS = 3600  # 1 hour
CLEANUP_PROBABILITY = 0.01  # 1% chance to run on a request

os.makedirs(TEMP_DIR, exist_ok=True)

# --- File Validation and Cleanup ---

def validate_image_file(file: UploadFile):
    # (Implementation is the same as before, removed for brevity)
    contents = file.file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File size is too large. Maximum size: {MAX_FILE_SIZE/1024/1024:.1f}MB")
    file.file.seek(0)
    content_type = file.content_type
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported file type. Allowed formats: {', '.join(ALLOWED_FORMATS)}")
    img_format = imghdr.what(None, h=contents)
    if img_format not in ALLOWED_FORMATS:
        raise HTTPException(status_code=400, detail="Invalid image file. Please upload a valid image.")
    if img_format not in ALLOWED_MIME_TYPES[content_type]:
        raise HTTPException(status_code=400, detail="File format and content type mismatch.")

def cleanup_file(path: str):
    """Safely remove a file if it exists."""
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Cleaned up file: {path}")
    except OSError as e:
        logger.error(f"Error cleaning up file {path}: {e}")

def cleanup_old_files():
    """Clean up temporary files older than CLEANUP_MAX_AGE_SECONDS."""
    logger.info(f"Running periodic cleanup in {TEMP_DIR}...")
    now = time.time()
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        try:
            if os.path.isfile(file_path):
                file_age = now - os.path.getmtime(file_path)
                if file_age > CLEANUP_MAX_AGE_SECONDS:
                    cleanup_file(file_path)
        except Exception as e:
            logger.error(f"Error during periodic cleanup of {file_path}: {e}")

# --- API Endpoint ---

@router.post("/preview",
    # (responses and summary are the same as before)
)
async def preview_photo(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    output_format: Optional[str] = Query("passport_eu", enum=list(PRESET_SIZES.keys())),
    custom_width: Optional[int] = Query(None, gt=0, le=2000),
    custom_height: Optional[int] = Query(None, gt=0, le=2000)
):
    # --- Periodic Cleanup Trigger ---
    if random.random() < CLEANUP_PROBABILITY:
        background_tasks.add_task(cleanup_old_files)

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

        # Add cleanup task for the processed file after the response is sent
        background_tasks.add_task(cleanup_file, processed_output_path)

        return FileResponse(
            processed_output_path,
            media_type="image/png",
            filename=f"processed_{output_format}.png"
        )

    except (FaceNotFoundError, MultipleFacesError, ImageReadError) as e:
        # (Error handling is the same as before)
        if isinstance(e, FaceNotFoundError):
            raise HTTPException(status_code=400, detail="Please ensure your face is clearly visible in the photo.")
        elif isinstance(e, MultipleFacesError):
            raise HTTPException(status_code=400, detail="Please use a photo with only one person.")
        else:
            raise HTTPException(status_code=400, detail="The uploaded image file is corrupted or invalid.")
    except PhotoProcessingError as e:
        logger.error(f"An unexpected processing error occurred for {input_path}. Error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during photo processing.")
    except Exception as e:
        logger.exception(f"A critical server error occurred for {input_path}. Error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred.")
    finally:
        # Always clean up the original uploaded file
        cleanup_file(input_path)
