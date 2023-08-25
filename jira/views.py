from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.urls import reverse
from django.views import View

from .models import Project

from .forms import ProjectForm


def index(request):
    return HttpResponse("this is clone jira software")


class ProjectView(View):
    def get(self, request):
        form = ProjectForm
        projects = Project.objects.all()
        context = {"projects": projects, "form": form}
        return render(request, "jira/index.html", context)

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_at = timezone.now()
            project.save()
            return HttpResponseRedirect(reverse("jira:projects"))
        return render(request, "jira/index.html", {"errors": form.errors})

