from django import forms
from .models import Equipo, Cliente


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = [
            'tipo_equipo', 'marca', 'modelo', 'estado',
            'relato_cliente', 'observaciones_adicionales'
        ]
        widgets = {
            'tipo_equipo': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'marca': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'modelo': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'estado': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'relato_cliente': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent', 'placeholder': 'Describe el problema reportado por el cliente...'}),
            'observaciones_adicionales': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent', 'placeholder': 'Observaciones adicionales del técnico...'}),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'correo', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'correo': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
            'telefono': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'}),
        }