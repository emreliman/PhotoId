from rembg import remove
from PIL import Image
import os

def test_background_removal():
    """
    'uploads' klasöründeki test portresinin arka planını kaldırır
    ve sonucu 'assets' klasörüne kaydeder.
    """
    # Proje ana dizinini temel alarak dosya yolları oluşturulur
    # Bu script backend klasöründen çalıştırılacağı için ../ ile üst dizine çıkılır
    input_path = os.path.join('..', 'uploads', 'test_portrait.jpg')
    output_path = os.path.join('..', 'assets', 'test_portrait_no_bg.png')
    
    # Çıktı klasörünün var olup olmadığını kontrol et, yoksa oluştur
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"'{output_dir}' klasörü oluşturuldu.")

    try:
        print(f"Giriş dosyası: '{input_path}'")
        input_image = Image.open(input_path)
    except FileNotFoundError:
        print(f"❌ HATA: Giriş dosyası bulunamadı: '{input_path}'")
        print("Lütfen 'uploads' klasöründe 'test_portrait.jpg' adında bir dosya olduğundan emin olun.")
        return

    print("Arka plan kaldırılıyor...")
    output_image = remove(input_image)
    
    print(f"Sonuç kaydediliyor: '{output_path}'")
    output_image.save(output_path)
    
    print("Arka plan kaldırma testi başarıyla tamamlandı!")
    print(f"Sonuç dosyası burada: '{output_path}'")

if __name__ == "__main__":
    test_background_removal()