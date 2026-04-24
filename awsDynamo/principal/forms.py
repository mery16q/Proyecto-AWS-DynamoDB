#encoding:utf-8
from django import forms
from datetime import date, timedelta

class LibroBusquedaIsbnForm(forms.Form):
    isbn = forms.CharField(label="ISBN", widget=forms.TextInput, required=True)
    
class LibroBusquedaAutorForm(forms.Form):
    autor = forms.CharField(label="Autor", widget=forms.TextInput, required=True)

class LibroBusquedaTituloForm(forms.Form):
    titulo = forms.CharField(label="Título", widget=forms.TextInput, required=True)

class UsuarioBusquedaIdForm(forms.Form):
    user_id = forms.CharField(label="ID de Usuario", widget=forms.TextInput, required=True)

class UsuarioBusquedaEmailForm(forms.Form):
    email = forms.CharField(label="Email", required=True)

class UsuarioBusquedaNombreForm(forms.Form):
    nombre = forms.CharField(label="Nombre", widget=forms.TextInput, required=True)

class ValoracionesUsuarioForm(forms.Form):
    user_id = forms.CharField(label="ID de Usuario", widget=forms.TextInput, required=True)

class LibroBusquedaTipoForm(forms.Form):
    TIPO_CHOICES = [
        ('FISICO', 'Físico'),
        ('EBOOK', 'Ebook'),
        ('AUDIO', 'Audiolibro')
    ]
    tipo_item = forms.ChoiceField(label="Tipo de Ítem", choices=TIPO_CHOICES, required=True)

class PoblarForm(forms.Form):
    num_libros = forms.IntegerField(
        label="Número de Libros",
        min_value=1,
        max_value=1000,
        initial=50,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    num_usuarios = forms.IntegerField(
        label="Número de Usuarios",
        min_value=1,
        max_value=500,
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    num_autores = forms.IntegerField(
        label="Número de Autores",
        min_value=1,
        max_value=200,
        initial=5,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class PrestamoForm(forms.Form):
    user_id = forms.CharField(
        label="ID de Usuario", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345'})
    )
    isbn = forms.CharField(
        label="ISBN del Libro", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 978...'})
    )
    fecha_inicio = forms.DateField(
        label="Fecha de Inicio",
        initial=date.today,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    fecha_fin = forms.DateField(
        label="Fecha de Devolución",
        initial=date.today() + timedelta(days=15),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )