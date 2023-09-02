from django import forms

from .models import Project, Notes, Task, Comments
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title"]


class SignUpForm(UserCreationForm):
    username = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "password1", "password2"]


class BoardForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ["name"]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "deadline", "notes_id", "responsible_id", "status_id"]

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super(TaskForm, self).__init__(*args, **kwargs)

        if project:
            self.fields['notes_id'].queryset = Notes.objects.filter(project_id=project)
            self.fields['responsible_id'].queryset = User.objects.filter(userproject__project_id=project.id, userproject__is_approved=True).all()


