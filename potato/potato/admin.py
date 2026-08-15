from django.contrib import admin

from infrastructure.models import Todo, User

admin.site.register(Todo, admin.ModelAdmin)

admin.site.register(User, admin.ModelAdmin)
