from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import api_router
from config import settings

app = FastAPI(title="Sturdy Potato API", version="1.0.0")

# Kept for non-browser-same-origin clients (e.g. a future mobile app). The web
# client is served same-origin below, so it does not rely on CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Serve the built SPA (Vite output) when it is present. In production the
# Docker image bundles the compiled client here; in local dev the client is
# served separately by Vite, so this directory is absent and we skip it.
# API routes live under /api and are matched before the frontend fallback.
if settings.frontend_dir.is_dir():
    app.frontend("/", directory=str(settings.frontend_dir))
