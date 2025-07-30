import cv2
import mediapipe as mp
import os

def test_face_detection():
    """
    'uploads' klasöründeki test portresinde yüz algılar,
    konsola koordinatları basar ve sonucu 'assets' klasörüne kaydeder.
    """
    # Proje ana dizinini temel alarak dosya yolları oluşturulur
    input_path = os.path.join('..', 'uploads', 'test_portrait.jpg')
    output_path = os.path.join('..', 'assets', 'test_portrait_face_detected.jpg')

    # Çıktı klasörünün var olup olmadığını kontrol et
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"'{output_dir}' klasörü oluşturuldu.")

    # MediaPipe Yüz Algılama modelini başlat
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

    # Görüntüyü oku
    try:
        print(f"Giriş dosyası: '{input_path}'")
        image = cv2.imread(input_path)
        if image is None:
            print(f"HATA: Görüntü dosyası okunamadı veya bozuk: '{input_path}'")
            return
    except Exception as e:
        print(f"HATA: Giriş dosyası okunamadı: '{input_path}'. Hata: {e}")
        return

    # Görüntüyü RGB'ye dönüştür
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    print("Yüz algılama işlemi yapılıyor...")
    results = face_detection.process(image_rgb)

    if not results.detections:
        print("Hiç yüz algılanamadı.")
        return

    print(f"{len(results.detections)} adet yüz algılandı.")

    # Algılanan yüzlerin etrafına kutu çiz
    annotated_image = image.copy()
    for detection in results.detections:
        bboxC = detection.location_data.relative_bounding_box
        ih, iw, _ = image.shape
        x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                     int(bboxC.width * iw), int(bboxC.height * ih)
        
        print(f"- Algılanan Yüz Koordinatları (x, y, w, h): ({x}, {y}, {w}, {h})")
        
        # Dikdörtgen çiz
        cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Sonucu kaydet
    print(f"Sonuç kaydediliyor: '{output_path}'")
    cv2.imwrite(output_path, annotated_image)

    print("Yüz algılama testi başarıyla tamamlandı!")
    print(f"Sonuç dosyası burada: '{output_path}'")


if __name__ == "__main__":
    test_face_detection()
