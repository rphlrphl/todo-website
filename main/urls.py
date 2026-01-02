from . import views
from django.urls import path, include
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    path("", views.team, name = 'team'),
    path("tasks", views.tasks, name = 'tasks'),
    path("accomplished_tasks", views.accomplished_tasks, name = 'accomplished-tasks'),
]
