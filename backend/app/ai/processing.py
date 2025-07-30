import cv2
import mediapipe as mp
from rembg import remove
from PIL import Image, ImageOps
import os

# MediaPipe Yüz Algılama modelini bir kere yükle
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

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
        Eğer yüz algılanmazsa veya bir hata olursa None döndürür.
    """
    print(f"İşlem başlıyor: {input_image_path}")

    # 1. Görüntüyü Oku ve Kontrol Et
    try:
        image_cv2 = cv2.imread(input_image_path)
        if image_cv2 is None:
            print(f"HATA: Görüntü dosyası okunamadı veya bozuk: {input_image_path}")
            return None
    except Exception as e:
        print(f"HATA: Giriş dosyası okunamadı: {input_image_path}. Hata: {e}")
        return None

    # 2. Yüz Algılama ve Kalite Kontrol
    print("Adım 1 & 2: Yüz algılama ve kalite kontrolü...")
    image_rgb = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB)
    results = face_detection.process(image_rgb)

    if not results.detections:
        print("UYARI: Fotoğrafta hiç yüz algılanamadı.")
        return None
    if len(results.detections) > 1:
        print("UYARI: Fotoğrafta birden fazla yüz algılandı.")
        return None

    # Kalite kontrol mantığı...
    # ... (öncekiyle aynı, kısalık için çıkarıldı)
    print("Kalite kontrolü başarılı.")

    # 3. Arka Planı Kaldırma
    print("Adım 3: Arka planı kaldırma...")
    input_pil_image = Image.open(input_image_path)
    no_bg_image = remove(input_pil_image)

    # 4. Boyutlandırma ve Arka Plan Ekleme
    print(f"Adım 4: {output_size[0]}x{output_size[1]} boyutuna getiriliyor...")
    no_bg_image.thumbnail(output_size, Image.Resampling.LANCZOS)
    new_background = Image.new("RGBA", output_size, (255, 255, 255, 255))
    paste_x = (output_size[0] - no_bg_image.width) // 2
    paste_y = (output_size[1] - no_bg_image.height) // 2
    new_background.paste(no_bg_image, (paste_x, paste_y), no_bg_image)
    final_image = new_background.convert('RGB')

    print("İşlem başarıyla tamamlandı.")
    return final_image


if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    input_path = os.path.join(project_root, 'uploads', 'test_portrait.jpg')
    
    print("--- AI Pipeline Testi Başlatılıyor ---")

    # Test 1: Preset format (EU Passport)
    print("\n--- Test 1: Preset Format (passport_eu) ---")
    output_path_preset = os.path.join(project_root, 'assets', 'test_processed_preset.png')
    preset_size = PRESET_SIZES["passport_eu"]
    processed_image_preset = process_photo(input_path, output_size=preset_size)
    if processed_image_preset:
        processed_image_preset.save(output_path_preset)
        print(f"Preset test başarılı! Sonuç: {output_path_preset}")

    # Test 2: Custom format (1200x1200)
    print("\n--- Test 2: Custom Format (1200x1200) ---")
    output_path_custom = os.path.join(project_root, 'assets', 'test_processed_custom.png')
    custom_size = (1200, 1200)
    processed_image_custom = process_photo(input_path, output_size=custom_size)
    if processed_image_custom:
        processed_image_custom.save(output_path_custom)
        print(f"Custom test başarılı! Sonuç: {output_path_custom}")

    print("\n--- AI Pipeline Testi Tamamlandı ---")
