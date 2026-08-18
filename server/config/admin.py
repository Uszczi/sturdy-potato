from django.contrib import admin

from infrastructure.models import Project, Todo, User

admin.site.register(Project, admin.ModelAdmin)
admin.site.register(Todo, admin.ModelAdmin)

admin.site.register(User, admin.ModelAdmin)
