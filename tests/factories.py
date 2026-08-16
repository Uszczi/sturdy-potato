from typing import Any

import factory

from infrastructure.models import Project, Todo, User


class UserFactory(factory.django.DjangoModelFactory[User]):
    class Meta:
        model = User

    username = factory.Sequence(lambda number: f"user-{number}")


class ProjectFactory(factory.django.DjangoModelFactory[Project]):
    class Meta:
        model = Project

    user: factory.SubFactory[Any, User] = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda number: f"Project {number}")


class TodoFactory(factory.django.DjangoModelFactory[Todo]):
    class Meta:
        model = Todo

    user: factory.SubFactory[Any, User] = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda number: f"Task {number}")
    description = ""
    completed = False
