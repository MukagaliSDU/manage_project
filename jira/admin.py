from django.contrib import admin

from .models import Project, UserProject, Status, Task, Notes

# Register your models here.

admin.site.register(Project)
admin.site.register(UserProject)
admin.site.register(Status)
admin.site.register(Task)
admin.site.register(Notes)
