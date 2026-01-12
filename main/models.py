from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import math

# Create your models here.

class Team(models.Model):

    ACTIVE = 'active'
    DELETED = 'deleted'

    CHOICES_STATUS = (
        (ACTIVE, 'Active'),
        (DELETED, 'Deleted')
    )

    title = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='teams', through='TeamMembership')
    created_by = models.ForeignKey(User, related_name='created_teams', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=CHOICES_STATUS, default=ACTIVE)

    invite_code = models.CharField(max_length=36, unique=True, blank=True, null=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
    
class TeamMembership(models.Model):
    ROLE_CHOICES = (
        ('supervisor', 'Supervisor'),
        ('member', 'Member')
    ) # role choices for each user

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices = ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'team') # so users can only have one role inside a team


class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('submitted', 'Submitted'), 
        ('revision', 'Revision'),
        ('accomplished', 'Accomplishsed')
    ) # available status for each task

    DIFFICULTY_CHOICES = (
        (1,'1 - Very Easy'),
        (2,'2 - Easy'),
        (3,'3 - Medium'),
        (4,'4 - Hard'),
        (5,'5 - Very Hard')
    )

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    task_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=120)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True,related_name='assigned_tasks')
    deadline = models.DateTimeField()
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=1)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.title} - Assigned to: {self.assigned_to}"
    
    @property
    def priority_score(self):
        now = timezone.now()
        time_diff = self.deadline - now
        days_remaining = time_diff.days

        if days_remaining <= 0:
            return 10
        
        raw_score = self.difficulty + (10/max(days_remaining, 1))

        return min(max(round(raw_score), 1), 10)