from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.views import View, generic

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.mail import send_mail

from django.contrib.auth.models import User
from .models import Project, UserProject, Notes, Task, Status

from .forms import ProjectForm, SignUpForm, BoardForm, TaskForm


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


def isUser(user: User, project: Project):
    member = UserProject.objects.filter(user_id=user, project_id=project).all()
    if member:
        return True
    return False


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
            notes_to_create = [
                Notes(name="To Do", project_id=project),
                Notes(name="In Progress", project_id=project),
                Notes(name="Done", project_id=project)
            ]
            Notes.objects.bulk_create(notes_to_create)
            return HttpResponseRedirect(reverse("jira:index"))
        return render(request, "jira/project/add_project.html", {"error_msg": form.errors})


# Project get board page and delete project
class ProjectDetailView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        project_members = User.objects.filter(userproject__project_id=project_id, userproject__is_approved=True).all()
        notes = Notes.objects.filter(project_id=project).all()
        tasks = Task.objects.filter(project_id=project).all()
        add_board_form = BoardForm()
        context = {"project": project, "project_members": project_members, "notes": notes, "board_form": add_board_form}
        return render(request, "jira/project/project.html", context)

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if request.user == project.author or request.user.has_perm("jira.delete_project"):
            project.delete()
        return redirect(reverse("jira:index"))


# add board to project
class BoardDetailView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if isUser(user=request.user, project=project):
            form = BoardForm(request.POST)
            if form.is_valid():
                board = form.save(commit=False)
                board.project_id = project
                board.save()
                return redirect(reverse("jira:project", args=(project_id, )))


class BoardDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if isUser(user=request.user, project=project):
            board_id = request.POST["board_id"]
            db_board = get_object_or_404(Notes, pk=board_id)
            db_board.delete()
            return redirect(reverse("jira:project", args=(project_id, )))
        return render(request, "jira/project/find_project.html")


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


class TaskView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        form = TaskForm(project=project)
        context = {"form": form, "project": project}
        return render(request, "jira/task/task.html", context)

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if isUser(user=request.user, project=project):
            form = TaskForm(request.POST, project=project)
            if form.is_valid():
                task = form.save(commit=False)
                task.created_at = timezone.now()
                task.created_by_id = request.user
                task.project_id = project
                task.save()
                return redirect(reverse("jira:project", args=(project_id,)))
            else:
                print("not work this form")
                print(form.errors)
            return render(request, "jira/project/project.html", {"project": project, "form": form})


class TaskDetailView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, project_id, task_id):
        task = get_object_or_404(Task, pk=task_id)
        project = get_object_or_404(Project, pk=project_id)
        notes = Notes.objects.filter(project_id=project).all()
        left_time = task.deadline - timezone.now()
        hours, remainder = divmod(left_time.seconds, 3600)
        minutes = divmod(remainder, 60)
        status = Status.objects.all()
        left_time = task.deadline - timezone.now()
        members = User.objects.filter(userproject__project_id=project_id, userproject__is_approved=True).all()
        if isUser(user=request.user, project=project):
            context = {"task": task, "notes": notes, "statuses": status, "members": members, "project": project,
                       "left_time_days": left_time.days,
                       "left_time_hours": hours,
                       "left_time_minutes": minutes,
                       }
            return render(request, "jira/task/detail.html", context)
        else:
            return HttpResponseForbidden("You are not authorized to view this task.")

    def post(self, request, project_id, task_id):
        task = get_object_or_404(Task, pk=task_id)
        change_note = request.POST.get('note')
        change_status = request.POST.get('status')
        change_user = request.POST.get("responsible_user")
        db_note = Notes.objects.filter(id=change_note).first()
        db_status = Status.objects.filter(id=change_status).first()
        db_user = User.objects.filter(id=change_user).first()
        task.notes_id = db_note
        task.status_id = db_status
        task.updated_at = timezone.now()
        task.responsible_id = db_user
        task.save()

        return self.get(request=request, project_id=project_id, task_id=task_id)

    @staticmethod
    def delete(request, project_id, task_id):
        task = get_object_or_404(Task, pk=task_id)
        if task.created_by_id == request.user:
            task.delete()
        return redirect(reverse("jira:project", args=(project_id,)))


class CommentCreateView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, project_id, task_id):
        pass
