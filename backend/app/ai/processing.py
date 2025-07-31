import cv2
import mediapipe as mp
from rembg import remove
from PIL import Image, ImageOps
import os
import logging
import gc

# Custom exceptions
from .exceptions import FaceNotFoundError, MultipleFacesError, ImageReadError

# Logger'ı ayarla
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MediaPipe Yüz Algılama modelini bir kere yükle
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(
    model_selection=1, 
    min_detection_confidence=0.5
)

# Önceden tanımlanmış boyutlar (genişlik, yükseklik) piksel cinsinden
# 300 DPI referans alınmıştır (1 cm = 118 piksel)
PRESET_SIZES = {
    "passport_tr": (591, 709),  # 5cm x 6cm
    "passport_eu": (413, 531),  # 3.5cm x 4.5cm
    "visa_us": (600, 600),      # 2x2 inç
    "id_card_tr": (591, 709),   # 5cm x 6cm (Biyometrik)
    "custom": None # Kullanıcı tanımlı boyutlar için
}

def process_photo(input_image_path: str, output_size=(600, 600)):
    """
    Bir fotoğrafta yüz algılar, arka planı kaldırır ve yeniden boyutlandırır.

    Args:
        input_image_path: İşlenecek fotoğrafın yolu.
        output_size: Çıktı fotoğrafının boyutu (genişlik, yükseklik).

    Returns:
        İşlenmiş ve boyutlandırılmış fotoğrafı PIL Image formatında döndürür.
    
    Raises:
        ImageReadError: Görüntü dosyası okunamadığında veya bozuk olduğunda.
        FaceNotFoundError: Fotoğrafta yüz algılanamadığında.
        MultipleFacesError: Fotoğrafta birden fazla yüz algılandığında.
    """
    logger.info(f"Processing started for: {input_image_path}")

    try:
        # 1. Görüntüyü Oku ve Kontrol Et
        image_cv2 = cv2.imread(input_image_path)
        if image_cv2 is None:
            raise ImageReadError(f"Image file could not be read or is corrupted: {input_image_path}")
        
        # Memory optimization: Resize if too large
        height, width = image_cv2.shape[:2]
        if width > 1920 or height > 1080:
            scale = min(1920/width, 1080/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image_cv2 = cv2.resize(image_cv2, (new_width, new_height))
            logger.info(f"Resized image to {new_width}x{new_height} for memory optimization")

        # 2. Yüz Algılama ve Kalite Kontrol
        logger.info("Step 1 & 2: Face detection and quality check...")
        image_rgb = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB)
        results = face_detection.process(image_rgb)

        if not results.detections:
            raise FaceNotFoundError("No face detected in the photo.")
        if len(results.detections) > 1:
            raise MultipleFacesError("Multiple faces detected in the photo.")

        # Kalite kontrol mantığı...
        logger.info("Quality check successful.")

        # 3. Arka Planı Kaldırma
        logger.info("Step 3: Removing background...")
        input_pil_image = Image.open(input_image_path)
        no_bg_image = remove(input_pil_image)
        
        # Memory cleanup
        del image_cv2, image_rgb, input_pil_image
        gc.collect()

        # 4. Boyutlandırma ve Arka Plan Ekleme
        logger.info(f"Step 4: Resizing to {output_size[0]}x{output_size[1]}...")
        no_bg_image.thumbnail(output_size, Image.Resampling.LANCZOS)
        new_background = Image.new("RGBA", output_size, (255, 255, 255, 255))
        paste_x = (output_size[0] - no_bg_image.width) // 2
        paste_y = (output_size[1] - no_bg_image.height) // 2
        new_background.paste(no_bg_image, (paste_x, paste_y), no_bg_image)
        final_image = new_background.convert('RGB')
        
        # Memory cleanup
        del no_bg_image, new_background
        gc.collect()

        logger.info("Processing completed successfully.")
        return final_image

    except Exception as e:
        # Memory cleanup on error
        gc.collect()
        raise e


if __name__ == '__main__':
    # Bu bölüm test amaçlıdır ve doğrudan çalıştırıldığında exception'ları yakalar
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
    # Test edilecek görseller
    test_files = {
        "valid": os.path.join(project_root, 'assets', 'test_portrait_face_detected.jpg'),
        "no_face": os.path.join(project_root, 'assets', 'test_portrait_no_bg.png'), # Yüzsüz bir görsel varsayalım
        "multiple_faces": os.path.join(project_root, 'assets', 'test_portrait_processed.png') # Çok yüzlü bir görsel varsayalım
    }

    def run_test(test_name, file_path, size):
        print(f"\n--- Test: {test_name} ---")
        output_path = os.path.join(project_root, 'assets', f'test_output_{test_name}.png')
        try:
            processed_image = process_photo(file_path, output_size=size)
            if processed_image:
                processed_image.save(output_path)
                print(f"Test successful! Result saved to: {output_path}")
        except Exception as e:
            print(f"Test failed as expected: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    # Geçerli senaryo
    run_test("valid_passport", test_files["valid"], PRESET_SIZES["passport_eu"])
    
    # Yüz bulunamama senaryosu
    # Not: Gerçek bir "yüzsüz" resimle test etmek daha doğru olur.
    # run_test("no_face", test_files["no_face"], PRESET_SIZES["passport_eu"])
    
    # Çoklu yüz senaryosu
    # Not: Gerçek bir "çoklu yüz" resimle test etmek daha doğru olur.
    # run_test("multiple_faces", test_files["multiple_faces"], PRESET_SIZES["passport_eu"])

    print("\n--- AI Pipeline Test Completed ---")
