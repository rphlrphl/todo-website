from django import forms
from .models import Team, Task

class CreateTeam(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['title']

class CreateTask(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'deadline', 'difficulty']
        widgets = {
            # This 'type': 'date' triggers the browser's native calendar picker
            'deadline': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            # You can also add classes to other fields for better Bootstrap styling
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'difficulty': forms.NumberInput(attrs={
                'class': 'form-control',
                'min' : 1,
                'max' : 5,
                'placeholder' : 'Scale 1-5'}),
        }