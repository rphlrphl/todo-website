from django import forms
from .models import Team

class CreateTeam(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['title']