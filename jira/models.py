from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
# Create your models here.


class Project(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='projects_authored')
    title = models.CharField(max_length=150)
    created_at = models.DateTimeField(default=timezone.now)
    users = models.ManyToManyField(User, through="UserProject")

    def __str__(self):
        return self.title


class UserProject(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)


class Notes(models.Model):
    name = models.CharField(max_length=150)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    deadline = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    notes_id = models.ForeignKey(Notes, on_delete=models.CASCADE)
    created_by_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    responsible_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responsible_tasks')
    status_id = models.ForeignKey(Status, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)


class Comments(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_comments_user')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recevie_comments_get_user')
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments_to_task')



