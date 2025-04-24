from django import forms
from .models import Camera
from django.contrib.auth.models import Group, Permission

class CameraForm(forms.ModelForm):
    class Meta:
        model = Camera
        fields = ['name', 'url', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-lg w-full py-5 px-9 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm transition duration-300',
                'placeholder': 'Nombre de la cámara',
            }),
            'url': forms.URLInput(attrs={
                'class': 'appearance-none border border-gray-300 rounded-lg w-full py-5 px-9 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm transition duration-300',
                'placeholder': 'http://ejemplo.com',
            }),
            'description': forms.Textarea(attrs={
                'class': 'appearance-none border border-gray-300 rounded-lg w-full py-5 px-9 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm transition duration-300',
                'placeholder': 'Descripción de la cámara',
                'rows': 4,
            }),
        }


class UserGroupPermissionForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'id': 'group-select'}),
        required=True
    )
    
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        fields = ['groups', 'permissions']








