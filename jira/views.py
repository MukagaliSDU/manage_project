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
    projects = Project.objects.filter(userproject__user_id=request.user, userproject__is_approved=True).order_by("-created_at").all()
    context = {
        "projects": projects
    }
    return render(request, "jira/index.html", context)


def get_user_project(request):
    return render(request, "jira/project/find_project.html")


def join_request(request, project_id: int):
    if request.method == 'POST':
        user = request.POST.get('user')
        action = request.POST.get('action')
        project = Project.objects.filter(id=project_id).first()
        user_project = UserProject.objects.filter(project_id=project, user_id=int(user)).first()
        if action == 'accept':
            user_project.is_approved = True
            user_project.save()
        elif action == 'reject':
            user_project.delete()

        return redirect(reverse("jira:user_project", args=(project_id, )))


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
            user_project = UserProject(user_id=request.user, project_id=project, is_approved=True)
            user_project.save()
            return HttpResponseRedirect(reverse("jira:index"))
        return render(request, "jira/project/add_project.html", {"error_msg": form.errors})


class ProjectDetailView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        project_members = User.objects.filter(userproject__project_id=project_id, userproject__is_approved=True).all()
        context = {"project": project, "project_members": project_members}
        return render(request, "jira/project/project.html", context)

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if request.user == project.author or request.user.has_perm("jira.delete_project"):
            project.delete()
        return redirect(reverse("jira:index"))


def is_member(self, user: User, project: Project):
    user = UserProject.objects.filter(user_id=user, project_id=project, is_approved=True).first()
    if user:
        return True
    return False


class SearchProjectView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        query_string = request.GET["title"]
        projects = []
        if query_string:
            projects = Project.objects.filter(title__icontains=query_string)
        context = {"projects": projects}
        return render(request, "jira/project/find_project.html", context)


class UserProjectView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, project_id):
        users = User.objects.filter(userproject__project_id=project_id, userproject__is_approved=False).all()
        project = Project.objects.get(id=project_id)
        context = {"users": users, "project": project}
        return render(request, "jira/project/members.html", context)

    def post(self, request, project_id):
        project = Project.objects.get(id=project_id)
        user_project = UserProject(user_id=request.user, project_id=project, is_approved=False)
        user_project.save()
        return HttpResponseRedirect(reverse("jira:searchPage"))


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

