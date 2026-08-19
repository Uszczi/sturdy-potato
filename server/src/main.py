from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import api_router
from config import settings
from infrastructure.admin import setup_admin
from use_cases.exceptions import UseCaseError

app = FastAPI(title="Sturdy Potato API", version="1.0.0")


@app.exception_handler(UseCaseError)
async def _use_case_error_handler(
    request: Request, exc: UseCaseError
) -> JSONResponse:
    # Map domain errors raised by use cases to HTTP responses, keeping the
    # {"detail": ...} shape FastAPI's HTTPException produces.
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# Kept for non-browser-same-origin clients (e.g. a future mobile app). The web
# client is served same-origin below, so it does not rely on CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# SQLAdmin database UI, mounted at /admin behind a login (see AdminAuth).
setup_admin(app)

# Serve the built SPA (Vite output) when it is present. In production the
# Docker image bundles the compiled client here; in local dev the client is
# served separately by Vite, so this directory is absent and we skip it.
# API routes live under /api and are matched before the frontend fallback.
if settings.frontend_dir.is_dir():
    app.frontend("/", directory=str(settings.frontend_dir))
