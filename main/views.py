from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .models import TeamMembership, Team, Task
from .ModelForm import CreateTeam
import uuid
from django.contrib.auth import logout
from django.contrib import auth

@login_required
def signout(request):
    logout(request)
    return redirect('/')

@login_required
def team_detail(request, team_id):
    # 1. Get the team or 404
    team = get_object_or_404(Team, id=team_id)
    
    # 2. Security: Check if the logged-in user is actually in this team
    user_membership = TeamMembership.objects.filter(user=request.user, team=team).first()
    
    if not user_membership:
        return redirect('main:profile') # Redirect if they try to snoop on other teams

    # 3. Get all members of this team to show in a list
    all_memberships = TeamMembership.objects.filter(team=team).select_related('user')

    # 4. Get tasks for this team
    tasks = team.tasks.all()

    context = {
        'team': team,
        'my_role': user_membership.role,
        'memberships': all_memberships,
        'tasks': tasks,
    }
    return render(request, 'main/team_detail.html', context)

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
    context = {}
    return render(request, "main/tasks.html", context)

@login_required
def accomplished_tasks(request):
    context = {}
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
