from fastapi import FastAPI
import uvicorn

# Basit FastAPI uygulaması
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/test")
def test_endpoint():
    return {"status": "success", "message": "API çalışıyor!"}

if __name__ == "__main__":
    print("🚀 Minimal FastAPI test başlatılıyor...")
    print("📡 Server: http://127.0.0.1:8080")
    print("📚 Docs: http://127.0.0.1:8080/docs")
    uvicorn.run(app, host="127.0.0.1", port=8080) 