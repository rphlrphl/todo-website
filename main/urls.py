from . import views
from django.urls import path, include
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    path("", views.team, name = 'team'),
    path("tasks", views.tasks, name = 'tasks'),
    path("accomplished_tasks", views.accomplished_tasks, name = 'accomplished-tasks'),
    path("team/<int:team_id>/", views.team_detail, name='team-detail'),
    path("team/<int:team_id>/invite/", views.generate_invite, name = 'generate-invite'),
    path("create-team", views.create_team, name = 'create-team'),
    path('join-team/', views.join_team, name='join-team'),
]
