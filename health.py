# health.py
from fastapi import FastAPI
import uvicorn, os

app = FastAPI()

@app.get("/")
def ok():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2000)
