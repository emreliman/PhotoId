import logging
import gc
from PIL import Image
import os

# Custom exceptions
from .exceptions import FaceNotFoundError, MultipleFacesError, ImageReadError

# Logger'ı ayarla
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    Geçici olarak basit bir resim işleme fonksiyonu.
    AI kütüphaneleri yüklendikten sonra tam fonksiyonalite eklenecek.
    """
    logger.info(f"Processing started for: {input_image_path}")

    try:
        # Basit resim işleme (AI kütüphaneleri olmadan)
        input_image = Image.open(input_image_path)
        
        # Resmi yeniden boyutlandır
        resized_image = input_image.resize(output_size, Image.Resampling.LANCZOS)
        
        # Beyaz arka plan oluştur
        background = Image.new('RGB', output_size, (255, 255, 255))
        
        # Resmi ortala
        paste_x = (output_size[0] - resized_image.width) // 2
        paste_y = (output_size[1] - resized_image.height) // 2
        background.paste(resized_image, (paste_x, paste_y))
        
        logger.info("Processing completed successfully (basic mode).")
        return background

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise ImageReadError(f"Failed to process image: {e}")


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
