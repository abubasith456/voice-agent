# health.py
from fastapi import FastAPI
import uvicorn, os

app = FastAPI()

@app.get("/")
def ok():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("HEALTH_PORT", "8081"))
    uvicorn.run(app, host="0.0.0.0", port=port)
