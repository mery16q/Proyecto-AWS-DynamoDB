#encoding:utf-8
from django.urls import path
from . import views

app_name = 'principal'

urlpatterns = [
    path('', views.index, name='index'),
    path('buscar-isbn/', views.buscar_isbn, name='buscar_isbn'),
    path('buscar-autor/', views.buscar_autor, name='buscar_autor'),
    path('buscar-tipo/', views.buscar_tipo, name='buscar_tipo'),
    path('poblar/', views.poblar_base_datos, name='poblar_base_datos'),
]
