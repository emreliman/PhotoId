import cv2
import mediapipe as mp
from rembg import remove
from PIL import Image, ImageOps
import os

# MediaPipe Yüz Algılama modelini bir kere yükle
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

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

    # 2. Yüz Algılama
    print("Adım 1: Yüz algılama...")
    image_rgb = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB)
    results = face_detection.process(image_rgb)

    if not results.detections:
        print("UYARI: Fotoğrafta hiç yüz algılanamadı. İşlem durduruldu.")
        return None
    
    print(f"{len(results.detections)} adet yüz algılandı.")

    # 2b. Kalite Kontrol
    print("Adım 2: Kalite kontrolü yapılıyor...")
    if len(results.detections) > 1:
        print("UYARI: Fotoğrafta birden fazla yüz algılandı. Lütfen tek bir yüz içeren bir fotoğraf kullanın.")
        return None

    detection = results.detections[0]
    bboxC = detection.location_data.relative_bounding_box
    ih, iw, _ = image_cv2.shape

    # Yüz boyutu kontrolü
    face_area = (bboxC.width * iw) * (bboxC.height * ih)
    image_area = ih * iw
    face_ratio = face_area / image_area
    
    MIN_FACE_RATIO = 0.05  # Yüzün, toplam alanın en az %5'i olması gerekir
    if face_ratio < MIN_FACE_RATIO:
        print(f"UYARI: Yüz çok küçük (Toplam alanın %{face_ratio * 100:.2f}'i). Lütfen daha yakın çekilmiş bir fotoğraf kullanın.")
        return None

    # Yüz konumu kontrolü (kenarlara değmemeli)
    EDGE_TOLERANCE = 0.01
    if bboxC.xmin < EDGE_TOLERANCE or bboxC.ymin < EDGE_TOLERANCE or \
       (bboxC.xmin + bboxC.width) > (1 - EDGE_TOLERANCE) or \
       (bboxC.ymin + bboxC.height) > (1 - EDGE_TOLERANCE):
        print("UYARI: Yüz, fotoğrafın kenarlarına çok yakın veya kesilmiş. Lütfen yüzün tamamen göründüğü bir fotoğraf kullanın.")
        return None
        
    print("Kalite kontrolü başarılı.")

    # 3. Arka Planı Kaldırma
    print("Adım 3: Arka planı kaldırma...")
    input_pil_image = Image.open(input_image_path)
    no_bg_image = remove(input_pil_image)

    # 4. Boyutlandırma ve Arka Plan Ekleme
    print(f"Adım 4: {output_size[0]}x{output_size[1]} boyutuna getiriliyor...")
    
    # Görüntüyü orantılı olarak küçült
    no_bg_image.thumbnail(output_size, Image.Resampling.LANCZOS)
    
    # Beyaz bir arka plan oluştur
    new_background = Image.new("RGBA", output_size, (255, 255, 255, 255))
    
    # Küçültülmüş görüntüyü arka planın ortasına yapıştır
    paste_x = (output_size[0] - no_bg_image.width) // 2
    paste_y = (output_size[1] - no_bg_image.height) // 2
    new_background.paste(no_bg_image, (paste_x, paste_y), no_bg_image)
    
    # Sonucu RGB'ye çevir (JPEG gibi formatlar için)
    final_image = new_background.convert('RGB')

    print("İşlem başarıyla tamamlandı.")
    return final_image


if __name__ == '__main__':
    # Bu script'i doğrudan test etmek için kullanılır.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
    input_path = os.path.join(project_root, 'uploads', 'test_portrait.jpg')
    output_path = os.path.join(project_root, 'assets', 'test_portrait_processed_resized.png')

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