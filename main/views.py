from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def team(request):
    context = {}
    return render(request, "main/team.html", context)

@login_required
def tasks(request):
    context = {}
    return render(request, "main/tasks.html", context)

@login_required
def accomplished_tasks(request):
    context = {}
    return render(request, "main/accomplished-tasks.html", context)
