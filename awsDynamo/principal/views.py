#encoding:utf-8
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import sys
import os

# Agregar la ruta src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from consultas import buscar_libro_por_isbn, buscar_por_autor, scan_por_tipo_item, obtener_tamano_tabla
from poblar_db import poblar_todo
from .forms import LibroBusquedaIsbnForm, LibroBusquedaAutorForm, LibroBusquedaTipoForm, PoblarBaseDatosForm


def index(request):
    """Vista de inicio con formularios de búsqueda."""
    contexto = {
        'form_isbn': LibroBusquedaIsbnForm(),
        'form_autor': LibroBusquedaAutorForm(),
        'form_tipo': LibroBusquedaTipoForm(),
    }
    return render(request, 'principal/index.html', contexto)


@require_http_methods(["GET", "POST"])
def buscar_isbn(request):
    resultados = []
    mensaje = ""
    tiempo = 0
    form = LibroBusquedaIsbnForm()
    
    if request.method == 'POST':
        form = LibroBusquedaIsbnForm(request.POST)
        if form.is_valid():
            isbn = form.cleaned_data['isbn']
            try:
                libro, tiempo = buscar_libro_por_isbn(isbn)
                if libro:
                    resultados = [libro]
                else:
                    mensaje = f"No se encontró libro con ISBN: {isbn}"
            except Exception as e:
                mensaje = f"Error en la búsqueda: {str(e)}"
    
    total_tabla = obtener_tamano_tabla()
    contexto = {
        'form': form,
        'resultados': resultados,
        'mensaje': mensaje,
        'tiempo': tiempo,
        'total_tabla': total_tabla,
        'tipo_busqueda': 'ISBN',
    }
    return render(request, 'principal/resultados.html', contexto)

@require_http_methods(["GET", "POST"])
def buscar_autor(request):
    resultados = []
    mensaje = ""
    tiempo = 0
    form = LibroBusquedaAutorForm()
    
    if request.method == 'POST':
        form = LibroBusquedaAutorForm(request.POST)
        if form.is_valid():
            autor = form.cleaned_data['autor']
            try:
                resultados, tiempo = buscar_por_autor(autor)
                if not resultados:
                    mensaje = f"No se encontraron libros del autor: {autor}"
            except Exception as e:
                mensaje = f"Error en la búsqueda: {str(e)}"
    
    total_tabla = obtener_tamano_tabla()
    contexto = {
        'form': form,
        'resultados': resultados,
        'mensaje': mensaje,
        'tiempo': tiempo,
        'total_tabla': total_tabla,
        'tipo_busqueda': 'Autor',
    }
    return render(request, 'principal/resultados.html', contexto)

@require_http_methods(["GET", "POST"])
def buscar_tipo(request):
    resultados = []
    mensaje = ""
    tiempo = 0
    form = LibroBusquedaTipoForm()
    
    if request.method == 'POST':
        form = LibroBusquedaTipoForm(request.POST)
        if form.is_valid():
            tipo_item = form.cleaned_data['tipo_item']
            try:
                resultados, tiempo = scan_por_tipo_item(tipo_item)
                if not resultados:
                    mensaje = f"No se encontraron items de tipo: {tipo_item}"
            except Exception as e:
                mensaje = f"Error en la búsqueda: {str(e)}"
    
    total_tabla = obtener_tamano_tabla()
    contexto = {
        'form': form,
        'resultados': resultados,
        'mensaje': mensaje,
        'tiempo': tiempo,
        'total_tabla': total_tabla,
        'tipo_busqueda': 'Tipo',
    }
    return render(request, 'principal/resultados.html', contexto)


@require_http_methods(["GET", "POST"])
def poblar_base_datos(request):
    """Vista para poblar la base de datos con libros aleatorios."""
    mensaje = ""
    form = PoblarBaseDatosForm()
    
    if request.method == 'POST':
        form = PoblarBaseDatosForm(request.POST)
        if form.is_valid():
            num_elementos = form.cleaned_data['num_elementos']
            try:
                poblar_todo(num_elementos)
                mensaje = f"¡Éxito! Se han creado {num_elementos} libros en la base de datos."
            except Exception as e:
                mensaje = f"Error al poblar la base de datos: {str(e)}"
    
    contexto = {
        'form': form,
        'mensaje': mensaje,
        'form_isbn': LibroBusquedaIsbnForm(),
        'form_autor': LibroBusquedaAutorForm(),
        'form_tipo': LibroBusquedaTipoForm(),
        'form_poblar': form,
    }
    return render(request, 'principal/poblar.html', contexto)