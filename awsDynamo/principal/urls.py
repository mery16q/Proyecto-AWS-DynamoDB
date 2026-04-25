#encoding:utf-8
from django.urls import path
from . import views

app_name = 'principal'

urlpatterns = [
    path('', views.index, name='index'),
    path('buscar-isbn/', views.buscar_isbn, name='buscar_isbn'),
    path('buscar-autor/', views.buscar_autor, name='buscar_autor'),
    path('buscar-titulo/', views.buscar_titulo, name='buscar_titulo'),
    path('buscar-usuario-id/', views.buscar_usuario_id, name='buscar_usuario_id'),
    path('buscar-usuario-email/', views.buscar_usuario_email, name='buscar_usuario_email'),
    path('buscar-usuario-nombre/', views.buscar_usuario_nombre, name='buscar_usuario_nombre'),
    path('buscar-valoraciones-usuario/', views.buscar_valoraciones_usuario, name='buscar_valoraciones_usuario'),
    path('buscar-prestamos-usuario/', views.buscar_prestamos_usuario, name='buscar_prestamos_usuario'),
    path('buscar-prestamos-isbn/', views.buscar_prestamos_isbn, name='buscar_prestamos_isbn'),
    path('buscar-tipo/', views.buscar_tipo, name='buscar_tipo'),
    path('editar-item/', views.editar_item, name='editar_item'),
    path('eliminar-item/', views.eliminar_item_view, name='eliminar_item'),
    path('registrar-prestamo/', views.registrar_prestamo, name='registrar_prestamo'),
    path('poblar/', views.poblar_base_datos, name='poblar_base_datos'),
]
