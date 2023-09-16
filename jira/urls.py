from django.urls import path

from . import views

app_name = "jira"
urlpatterns = [

  path("", views.index, name="index"),
  path("projects/", views.ProjectView.as_view(), name="projects"),
  path("projects/<int:project_id>/", views.ProjectDetailView.as_view(), name="project"),
  path("projects/<int:project_id>/add/board/", views.BoardDetailView.as_view(), name="add_board"),
  path("project/<int:project_id>/remove/board/", views.BoardDetailView.delete, name="remove_board"),
  path("sign-up/", views.SignUpView.as_view(), name="signup"),
  path("my_task/", views.user_tasks, name="user_task"),
  path("project/find/", views.get_user_project, name="searchPage"),
  path("projects/search", views.SearchProjectView.as_view(), name="search"),
  path("project/<int:project_id>/add/", views.UserProjectView.as_view(), name="user_project"),
  path('project/<int:project_id>/join/', views.join_request, name='join_project'),
  path('project/<int:project_id>/task/add/', views.TaskView.as_view(), name="task"),
  path('project/<int:project_id>/task/<int:task_id>/', views.TaskDetailView.as_view(), name="task_detail"),
  path('project/<int:project_id>/task/<int:task_id>/delete/', views.TaskDetailView.delete, name="task_delete"),

]