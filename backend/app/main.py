from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import uploads, validations

app = FastAPI(title="Warehouse Product Verifier", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers must be registered before static mounts to avoid path conflicts
app.include_router(uploads.router)
app.include_router(validations.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Static file serving for uploaded images (local dev) — mounted last
media_dir = Path("uploads/images")
media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory="uploads/images"), name="media")
