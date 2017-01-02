#encoding:utf-8
from django import forms

class UsuarioBusquedaForm(forms.Form):
    idUsuario = forms.CharField(label="Id de Usuario", widget=forms.TextInput, required=True)
    
class UsuarioRecomendacionForm(forms.Form):
    idUsuario = forms.CharField(label="Id de Usuario", widget=forms.TextInput, required=True)