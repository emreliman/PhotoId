import cv2
import mediapipe as mp
from rembg import remove
from PIL import Image
import os
import numpy as np

# MediaPipe Yüz Algılama modelini bir kere yükle
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

def process_photo(input_image_path: str):
    """
    Bir fotoğrafta yüz algılar, ardından arka planı kaldırır.

    Args:
        input_image_path: İşlenecek fotoğrafın yolu.

    Returns:
        İşlenmiş fotoğrafı PIL Image formatında döndürür.
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

    # 2. Yüz Algılama
    print("Adım 1: Yüz algılama...")
    image_rgb = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB)
    results = face_detection.process(image_rgb)

    if not results.detections:
        print("UYARI: Fotoğrafta hiç yüz algılanamadı. İşlem durduruldu.")
        return None
    
    print(f"{len(results.detections)} adet yüz algılandı. Arka plan temizleme adımına geçiliyor.")

    # 3. Arka Planı Kaldırma
    print("Adım 2: Arka planı kaldırma...")
    # rembg, PIL Image nesnesi ile daha iyi çalışır
    input_pil_image = Image.open(input_image_path)
    output_pil_image = remove(input_pil_image)

    print("İşlem başarıyla tamamlandı.")
    return output_pil_image


if __name__ == '__main__':
    # Bu script'i doğrudan test etmek için kullanılır.
    # Script'in konumu: backend/app/ai/processing.py
    # Bu yüzden proje ana dizinine ulaşmak için 3 seviye yukarı çıkmalıyız.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
    input_path = os.path.join(project_root, 'uploads', 'test_portrait.jpg')
    output_path = os.path.join(project_root, 'assets', 'test_portrait_processed.png')

    print("--- AI Pipeline Testi Başlatılıyor ---")
    
    # Ana işlem fonksiyonunu çağır
    processed_image = process_photo(input_path)

    # Sonucu kaydet
    if processed_image:
        print(f"Sonuç kaydediliyor: {output_path}")
        processed_image.save(output_path)
        print(f"Test başarılı! İşlenmiş dosya burada: {output_path}")
    else:
        print("Test başarısız. İşlenmiş bir görüntü oluşturulamadı.")
    
    print("--- AI Pipeline Testi Tamamlandı ---")
