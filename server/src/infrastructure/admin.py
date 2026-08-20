from typing import ClassVar

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlmodel import col, select
from starlette.requests import Request

from config import settings
from infrastructure.db import async_session_maker, engine
from infrastructure.models import Project, Task, User
from infrastructure.security import password_hasher


class AdminAuth(AuthenticationBackend):
    """Gate the admin behind the existing user credentials.

    Only active users with the is_staff flag may sign in.
    """

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if not isinstance(username, str) or not isinstance(password, str):
            return False
        async with async_session_maker() as session:
            user = await session.scalar(
                select(User).where(col(User.username) == username)
            )
        if user is None or not user.is_active or not user.is_staff:
            return False
        if not await password_hasher.verify(password, user.hashed_password):
            return False
        request.session["admin_user"] = user.username
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "admin_user" in request.session


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    column_list: ClassVar = ["id", "username", "is_active", "is_staff"]
    column_details_exclude_list: ClassVar = ["hashed_password"]
    form_excluded_columns: ClassVar = ["hashed_password"]


class ProjectAdmin(ModelView, model=Project):
    name = "Project"
    name_plural = "Projects"
    icon = "fa-solid fa-folder"
    column_list: ClassVar = ["id", "user_id", "name", "color", "position"]


class TaskAdmin(ModelView, model=Task):
    name = "Task"
    name_plural = "Tasks"
    icon = "fa-solid fa-list-check"
    column_list: ClassVar = ["id", "user_id", "title", "completed", "due_date"]


def setup_admin(app: FastAPI) -> Admin:
    admin = Admin(
        app,
        engine,
        authentication_backend=AdminAuth(secret_key=settings.secret_key),
    )
    admin.add_view(UserAdmin)
    admin.add_view(ProjectAdmin)
    admin.add_view(TaskAdmin)
    return admin
