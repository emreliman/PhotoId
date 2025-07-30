# PhotoID AI

Bağımsız AI destekli kimlik/pasaport fotoğrafı düzenleme platformu.

## 🚀 Özellikler

- **AI Destekli Fotoğraf İşleme**: Yüz algılama ve arka plan kaldırma
- **Otomatik Boyutlandırma**: Kimlik, pasaport ve vize fotoğrafı formatları
- **Kalite İyileştirme**: Parlaklık, kontrast ve keskinlik ayarları
- **Hızlı İşleme**: 30 saniyede tamamlanan işlem süresi
- **Güvenli Yükleme**: Dosya doğrulama ve güvenlik kontrolleri

## 📋 Gereksinimler

- Python 3.9+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

## 🛠️ Kurulum

### 1. Repository'yi klonlayın
```bash
git clone <repository-url>
cd PhotoId
```

### 2. Backend kurulumu
```bash
cd backend

# Virtual environment oluşturun
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows

# Dependencies yükleyin
pip install -r requirements.txt

# Environment dosyasını kopyalayın
cp env.example .env
# .env dosyasını düzenleyin
```

### 3. Docker ile çalıştırma
```bash
# Tüm servisleri başlatın
docker-compose up -d

# Backend API: http://localhost:8000
# PostgreSQL: localhost:5432
# Redis: localhost:6379
```

### 4. Geliştirme modunda çalıştırma
```bash
# Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Dokümantasyonu

API dokümantasyonuna şu adresten erişebilirsiniz:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Test

```bash
cd backend
pytest
```

## 📁 Proje Yapısı

```
PhotoId/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Konfigürasyon
│   │   ├── db/           # Database utilities
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic
│   │   └── ai/           # AI processing
│   ├── tests/            # Test dosyaları
│   ├── docker/           # Docker dosyaları
│   └── requirements.txt
├── frontend/             # React/Next.js frontend
└── README.md
```

## 🔧 Geliştirme

### Backend Geliştirme
- FastAPI framework kullanılıyor
- SQLAlchemy ORM ile PostgreSQL
- Celery ile background processing
- Redis cache sistemi

### AI Pipeline
- MediaPipe ile yüz algılama
- U²-Net ile arka plan kaldırma
- OpenCV ile görsel işleme
- PyTorch ile model optimizasyonu

## 📈 Performans Hedefleri

- **İşleme Süresi**: <30 saniye
- **API Yanıt Süresi**: <2 saniye
- **Uptime**: >99.5%
- **Eşzamanlı Kullanıcı**: 100+

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

- **Proje Sahibi**: [İsim]
- **Email**: [email@example.com]
- **Website**: [website.com]

---

**Geliştirme Durumu**: Aktif Geliştirme
**Son Güncelleme**: 29 Temmuz 2025 