
from django.contrib import admin

# Register your models here.

from .models import Team, TeamMembership, Task

# admin.site.register(Team)
# admin.site.register(TeamMembership)
# admin.site.register(Task)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('title',)

# This makes the Membership visible (great for checking roles)
@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'role')
    list_filter = ('role', 'team')

# This makes the Tasks visible
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'task_id',
        'title',
        'team',
        'status',
        'deadline',
        'created_by',
        'priority_score_display',
    )
    list_filter = ('status', 'team')

    def priority_score_display(self, obj):
        return obj.priority_score

    priority_score_display.short_description = 'Priority Score'
    priority_score_display.admin_order_field = 'deadline'