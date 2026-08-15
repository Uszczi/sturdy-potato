from potato.models import User
from django.contrib import admin

from infrastructure.models import Todo

admin.site.register(Todo, admin.ModelAdmin)

admin.site.register(User, admin.ModelAdmin)
