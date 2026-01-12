from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

# Create your views here.

from django.views.decorators.cache import never_cache

@never_cache
@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return redirect("main:team")
        
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("main:team")
    else:
        form = AuthenticationForm()

    return render(request, "myApp/login.html", {"form": form})

@ensure_csrf_cookie
def session_status(request):
    return JsonResponse({'logged_in': request.user.is_authenticated})

def signup(response):
    # context = {}
    if response.method == "POST":
        form = UserCreationForm(response.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = UserCreationForm()
    return render(response, "myApp/signup.html", {"form":form})
