from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.views import View, generic

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


from django.contrib.auth.models import User
from .models import Project, UserProject

from .forms import ProjectForm, SignUpForm


@login_required(login_url="/login/")
def index(request):
    projects = Project.objects.order_by("-created_at").all()
    context = {
        "projects": projects
    }
    return render(request, "jira/index.html", context)


class ProjectView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        form = ProjectForm
        projects = Project.objects.all()
        context = {"projects": projects, "form": form}
        return render(request, "jira/project/add_project.html", context)


    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.author = request.user
            project.created_at = timezone.now()
            project.save()
            return HttpResponseRedirect(reverse("jira:index"))
        return render(request, "jira/project/add_project.html", {"error_msg": form.errors})


class ProjectDetailView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        project_members = project_members = User.objects.filter(userproject__project_id=project_id, userproject__is_approved=True).all()
        print(f"project_members: {project_members}")
        context = {"project": project, "project_members": project_members}
        return render(request, "jira/project/project.html", context)

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if request.user == project.author or request.user.has_perm("jira.delete_project"):
            project.delete()
        return redirect(reverse("jira:index"))


class SignUpView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, "registration/sign_up.html", {"form": form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("jira:index", ))

        return render(request, "registration/sign_up.html", {"form": form})

