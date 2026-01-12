from django.db import models
from django.contrib.auth.models import User

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
        ('revision', 'Revision'),
        ('accomplished', 'Accomplishsed')
    ) # available status for each task

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.title