from app.main_simple import app
import uvicorn

if __name__ == "__main__":
    print("🚀 PhotoID AI Server başlatılıyor...")
    print("📡 URL: http://127.0.0.1:8080")
    print("📚 Docs: http://127.0.0.1:8080/docs")
    print("🔍 Health: http://127.0.0.1:8080/health")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info") 