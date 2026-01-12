from . import views
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path("", views.login_view, name = 'login'),
    path("signup", views.signup, name = 'signup'),
    path('session-status/', views.session_status, name='session_status'),
    path('accounts', include("django.contrib.auth.urls")),
    path('signout/', auth_views.LogoutView.as_view(next_page='login'), name='signout'),
]
