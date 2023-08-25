from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
# Create your models here.


class Project(models.Model):
    # author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    created_at = models.DateTimeField(default=timezone.now())
    users = models.ManyToManyField(User, through="UserProject")

    def __str__(self):
        return self.title


class UserProject(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)