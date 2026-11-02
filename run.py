"""Single command to start SuperChat:  python run.py   -> open http://localhost:8000"""
import uvicorn

from app.config import settings

if __name__ == "__main__":
    print(f"SuperChat running at http://localhost:{settings.port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port)
