from django.urls import path

from . import views

app_name = "jira"
urlpatterns = [

  path("", views.index, name="index"),

]