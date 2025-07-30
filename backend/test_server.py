from fastapi import FastAPI
import uvicorn

app = FastAPI(title="PhotoID AI Test")

@app.get("/")
async def root():
    return {"message": "PhotoID AI API Test", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080) 