from fastapi import APIRouter

from . import auth, projects, tasks, time

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(tasks.router)
api_router.include_router(projects.router)
api_router.include_router(time.router)
