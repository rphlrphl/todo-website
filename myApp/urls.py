from . import views
from django.urls import path, include

urlpatterns = [
    path("", views.login_view, name = 'login'),
    path("signup", views.signup, name = 'signup'),
    path('accounts', include("django.contrib.auth.urls"))
]
