#encoding:utf-8
from django import forms
   
class LibroBusquedaIsbnForm(forms.Form):
    isbn = forms.IntegerField(label="ISBN", widget=forms.NumberInput, required=True)
    
class LibroBusquedaAutorForm(forms.Form):
    autor = forms.CharField(label="Autor", widget=forms.TextInput, required=True)

class LibroBusquedaTipoForm(forms.Form):
    TIPO_CHOICES = [
        ('FISICO', 'Físico'),
        ('EBOOK', 'Ebook'),
        ('AUDIO', 'Audiolibro')
    ]
    tipo_item = forms.ChoiceField(label="Tipo de Ítem", choices=TIPO_CHOICES, required=True)