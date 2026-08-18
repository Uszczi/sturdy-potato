from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes import auth, projects, tasks

app = FastAPI(title="Sturdy Potato API", version="1.0.0")

# Cross-origin requests from the Vite dev/preview server (React SPA on another
# origin). Bearer tokens travel in the Authorization header, so credentialed
# cookies are not required.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(projects.router)
