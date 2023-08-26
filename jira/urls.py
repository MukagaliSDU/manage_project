from django.urls import path

from . import views

app_name = "jira"
urlpatterns = [

  path("", views.index, name="index"),
  path("projects/", views.ProjectView.as_view(), name="projects"),
  path("projects/<int:project_id>", views.ProjectDetailView.as_view(), name="project"),
  path("sign-up/", views.SignUpView.as_view(), name="signup"),


]