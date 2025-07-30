import requests
import asyncio
import aiohttp
import time

API_URL = "http://127.0.0.1:8000/api/v1/photos/preview"
TEST_IMAGE_PATH = "../uploads/test_portrait.jpg"

async def test_rate_limit():
    print("🚀 Rate Limit Testi Başlatılıyor...")
    
    params = {'output_format': 'passport_eu'}

    async def make_request(session, file_path):
        data = aiohttp.FormData()
        data.add_field('file',
                      open(file_path, 'rb'),
                      filename='test.jpg',
                      content_type='image/jpeg')
        return await session.post(API_URL, data=data, params=params)

    # İlk request (senkron)
    print("\n1️⃣ İlk request yapılıyor...")
    files = {'file': ('test.jpg', open(TEST_IMAGE_PATH, 'rb'), 'image/jpeg')}
    response = requests.post(API_URL, files=files, params=params)
    print(f"✓ İlk request sonucu: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.json()}")

    # Asenkron olarak hızlıca 4 request daha yap (saatlik limit aşımı)
    print("\n2️⃣ Saatlik limit testi (3 limit, 4 istek)...")
    async with aiohttp.ClientSession() as session:
        tasks = [make_request(session, TEST_IMAGE_PATH) for _ in range(4)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, resp in enumerate(responses, 1):
            if isinstance(resp, Exception):
                print(f"Request {i}: Hata - {resp}")
            else:
                if resp.status == 200:
                    # Başarılı response PNG dosyası döner
                    content = await resp.read()
                    print(f"Request {i}: {resp.status} - Başarılı (PNG dosyası alındı)")
                else:
                    # Hata durumunda JSON döner
                    error_json = await resp.json()
                    print(f"Request {i}: {resp.status} - {error_json}")

    print("\n✅ Rate limit testi tamamlandı!")

if __name__ == "__main__":
    asyncio.run(test_rate_limit())
