from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import api_router
from config import settings

app = FastAPI(title="Sturdy Potato API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)
