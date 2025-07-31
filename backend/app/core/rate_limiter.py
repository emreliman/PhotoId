from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
import time
from app.core.config import settings

class RateLimiter:
    def __init__(self):
        # Her IP için istek sayılarını tutan sözlükler
        self.daily_requests = defaultdict(list)  # günlük limit için
        self.hourly_requests = defaultdict(list)  # saatlik limit için
        
        # Limitleri tanımla
        self.DAILY_LIMIT = 10  # günlük maksimum istek
        self.HOURLY_LIMIT = 3  # saatlik maksimum istek

    def _cleanup_old_requests(self, ip: str):
        """Süresi dolmuş istekleri temizle"""
        now = datetime.now()
        
        # 24 saatten eski istekleri temizle
        day_ago = now - timedelta(days=1)
        self.daily_requests[ip] = [ts for ts in self.daily_requests[ip] if ts > day_ago]
        
        # 1 saatten eski istekleri temizle
        hour_ago = now - timedelta(hours=1)
        self.hourly_requests[ip] = [ts for ts in self.hourly_requests[ip] if ts > hour_ago]

    def check_rate_limit(self, request: Request):
        """Rate limit kontrolü yap"""
        # Test modunda rate limit kontrolü yapma
        if settings.TEST_MODE:
            return True
        ip = request.client.host
        now = datetime.now()
        
        # Eski istekleri temizle
        self._cleanup_old_requests(ip)
        
        # Mevcut istek sayılarını kontrol et
        daily_count = len(self.daily_requests[ip])
        hourly_count = len(self.hourly_requests[ip])
        
        # Limit kontrolü
        if daily_count >= self.DAILY_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Günlük fotoğraf işleme limitine ulaştınız (10 fotoğraf/gün). 24 saat içinde tekrar deneyiniz."
            )
        
        if hourly_count >= self.HOURLY_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Saatlik fotoğraf işleme limitine ulaştınız (3 fotoğraf/saat). 1 saat içinde tekrar deneyiniz."
            )
        
        # İsteği kaydet
        self.daily_requests[ip].append(now)
        self.hourly_requests[ip].append(now)

# Global rate limiter instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limit middleware"""
    # Sadece photo preview endpoint'i için rate limit uygula
    try:
        if request.url.path == "/api/v1/photos/preview":
            rate_limiter.check_rate_limit(request)
        response = await call_next(request)
        return response
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
