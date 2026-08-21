from fastapi import APIRouter

from . import auth, chat, comments, projects, register, tasks, time, workspaces

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(register.router)
api_router.include_router(workspaces.router)
api_router.include_router(tasks.router)
api_router.include_router(comments.router)
api_router.include_router(projects.router)
api_router.include_router(time.router)
api_router.include_router(chat.router)
