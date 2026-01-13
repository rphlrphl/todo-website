from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .models import TeamMembership, Team, Task
from .ModelForm import CreateTeam, CreateTask
import uuid
from django.contrib.auth import logout
from django.contrib import auth
from .utils import TaskMaxHeap, Stack
from django.core.paginator import Paginator


@login_required
def signout(request):
    logout(request)
    return redirect('/')

@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    user_membership = TeamMembership.objects.filter(user=request.user, team=team).first()
    if not user_membership:
        return redirect('main:profile') # Redirect if they try to snoop on other teams
    
# 1. Handle Form Submission (POST)
    if request.method == "POST":
        form = CreateTask(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.team = team
            task.save()
            messages.success(request, "Task added successfully!")
            return redirect('main:team-detail', team_id=team.id)
        # If form is NOT valid, it falls through to the bottom and 
        # is passed to context with error messages included.
    
    # 2. Handle Page Load (GET)
    else:
        form = CreateTask()
    
    # 3. Apply the Queryset Limit (Does not exist for GET and POST failure)
    # Ensure 'members' is a ManyToManyField on Team, or use the filter method discussed earlier
    if hasattr(team, 'members'):
        form.fields['assigned_to'].queryset = team.members.all()

    # heap logic
    pending_tasks = team.tasks.filter(status__in=['pending', 'submitted', 'revision'])
    task_heap = TaskMaxHeap(pending_tasks)
    sorted_tasks = task_heap.get_sorted_tasks()

    paginator = Paginator(sorted_tasks, 5) # Show 5 tasks per page
    page_number = request.GET.get('page')
    tasks_page = paginator.get_page(page_number)

    team_accomplished = team.tasks.filter(status='accomplished').order_by('updated_at')
    task_stack = Stack(team_accomplished)
    display_stack = task_stack.get_task_stack()

    acc_paginator = Paginator(display_stack, 5)
    acc_page_number = request.GET.get('acc_page') 
    acc_tasks_page = acc_paginator.get_page(acc_page_number)

    all_memberships = TeamMembership.objects.filter(team=team).select_related('user')
    # tasks = team.tasks.all()


    context = {
        'team': team,
        'my_role': user_membership.role,
        'memberships': all_memberships,
        'tasks': tasks_page,
        'form': form,
        'acc_stack': acc_tasks_page, 
        'acc_tasks': acc_tasks_page,
    }
    return render(request, 'main/team_detail.html', context)

@login_required
def complete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, task_id=task_id)
        
        # Security Check: Ensure only the supervisor of this team can complete it
        membership = TeamMembership.objects.filter(user=request.user, team=task.team).first()
        if not membership or membership.role != 'supervisor':
            messages.error(request, "You do not have permission to approve tasks.")
            return redirect('main:team-detail', team_id=task.team.id)

        # Update status
        task.status = 'accomplished'
        task.save()
        
        messages.success(request, f"Task '{task.title}' has been approved and moved to accomplished.")
        
    return redirect('main:team-detail', team_id=task.team.id)

@login_required
def submit_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, task_id=task_id)
        
        # Get the updated description from the POST data
        new_description = request.POST.get('description')
        
        task.status = 'submitted'
        if new_description:
            task.description = new_description
        
        task.save()
        messages.success(request, f"Task {task_id} submitted successfully!")

    # Redirect back to the team detail page or tasks list
    # Use task.team.id to stay on the same team page if preferred
    return redirect('main:tasks')

@login_required
def revise_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, task_id=task_id)
        
        new_description = request.POST.get('description')
        new_deadline = request.POST.get('deadline')
        
        task.status = 'revision' # Assuming 'revision' is your status code
        if new_description:
            task.description = new_description
        if new_deadline:
            task.deadline = new_deadline
        
        task.save()
        messages.warning(request, f"Task {task_id} sent back for revision.")

    return redirect('main:team-detail', team_id=task.team.id)

@login_required
def team(request):
    memberships = TeamMembership.objects.filter(user=request.user)
    context = {
        'memberships' : memberships,
        'has_team' : memberships.exists()
    }
    return render(request, "main/team.html", context)

@login_required
def tasks(request):
    # Use __in to fetch both pending and submitted tasks
    my_tasks = Task.objects.filter(
        assigned_to=request.user, 
        status__in=['pending', 'submitted', 'revision'] 
    )
    
    # Feed them into your Max-Heap logic
    task_heap = TaskMaxHeap(my_tasks)
    sorted_tasks = task_heap.get_sorted_tasks()

    context = {
        'tasks': sorted_tasks,
    }
    return render(request, "main/tasks.html", context)

@login_required
def accomplished_tasks(request):

    my_tasks = Task.objects.filter(
        assigned_to=request.user,
        status='accomplished'
    ).order_by('updated_at')

    task_stack = Stack(my_tasks)
    display_stack = task_stack.get_task_stack()

    paginator = Paginator(display_stack, 5) # Show 5 tasks per page
    page_number = request.GET.get('page')
    tasks_page = paginator.get_page(page_number)

    context = {
        'tasks' : tasks_page,
        'stack' : tasks_page
    }
    return render(request, "main/accomplished-tasks.html", context)

@login_required
def create_team(request):
    context = {}
    if request.method == 'POST':
        form = CreateTeam(request.POST)
        if form.is_valid:
            team = form.save(commit=False)
            team.created_by = request.user
            team.invite_code = str(uuid.uuid4())
            team.save()

            TeamMembership.objects.create(
                user = request.user,
                team = team,
                role = 'supervisor'
            )
            return redirect('main:team')
    else:
        form = CreateTeam()
    return render(request, 'main/create-team.html', {'form' : form})

@login_required
def generate_invite(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    # Only supervisors can generate invites
    membership = TeamMembership.objects.filter(user=request.user, team=team).first()
    if not membership or membership.role != 'supervisor':
        return JsonResponse({'error': 'Forbidden'}, status=403)

    # Save invite code if none exists
    if not team.invite_code:
        import uuid
        team.invite_code = str(uuid.uuid4())
        team.save()

    return JsonResponse({'invite_code': team.invite_code})

@login_required
def join_team(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        code = request.POST.get('code', '').strip()
        if not code:
            return JsonResponse({'error': "Please enter an invite code."})

        try:
            team = Team.objects.get(invite_code=code)
        except Team.DoesNotExist:
            return JsonResponse({'error': "Invalid invite code."})

        membership, created = TeamMembership.objects.get_or_create(
            user=request.user,
            team=team,
            defaults={'role': 'member'}
        )

        if created:
            return JsonResponse({'success': f"You joined {team.title} successfully!"})
        else:
            return JsonResponse({'info': "You are already a member of this team."})

    return JsonResponse({'error': "Invalid request."}, status=400)
