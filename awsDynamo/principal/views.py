# encoding:utf-8
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.core.cache import cache # Para optimizar el tamaño de la tabla
import sys
import os

# Configuración de ruta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Importaciones de consultas
from consultas import (
    buscar_libro_por_isbn,
    buscar_por_atributo_batch, 
    buscar_libros_por_titulo,  
    buscar_por_autor, 
    buscar_usuario_por_id,
    buscar_usuario_por_email,
    consultar_valoraciones_por_usuario, 
    buscar_por_tipo_item,
    obtener_item,
    actualizar_item,
    obtener_total_libros,
    obtener_total_usuarios,
    obtener_total_valoraciones,
    registrar_prestamo_transaccional
)
from poblar_db import poblar_todo
from .forms import (
    LibroBusquedaIsbnForm, 
    LibroBusquedaAutorForm, 
    LibroBusquedaTituloForm,
    PrestamoForm, 
    UsuarioBusquedaIdForm, 
    UsuarioBusquedaEmailForm, 
    UsuarioBusquedaNombreForm, 
    ValoracionesUsuarioForm, 
    LibroBusquedaTipoForm,
    PoblarForm,
)

def get_cached_entity_count(cache_key, fetcher):
    total = cache.get(cache_key)
    if total is None:
        total = fetcher()
        cache.set(cache_key, total, 3600)
    return total


def get_cached_book_count():
    return get_cached_entity_count('dynamodb_total_libros', obtener_total_libros)


def get_cached_user_count():
    return get_cached_entity_count('dynamodb_total_usuarios', obtener_total_usuarios)


def get_cached_rating_count():
    return get_cached_entity_count('dynamodb_total_valoraciones', obtener_total_valoraciones)

# --- VISTAS ---

def index(request):
    contexto = {
        'form_isbn': LibroBusquedaIsbnForm(),
        'form_autor': LibroBusquedaAutorForm(),
        'form_titulo': LibroBusquedaTituloForm(),
        'form_usuario_id': UsuarioBusquedaIdForm(),
        'form_usuario_email': UsuarioBusquedaEmailForm(),
        'form_usuario_nombre': UsuarioBusquedaNombreForm(),
        'form_valoraciones': ValoracionesUsuarioForm(),
        'form_tipo': LibroBusquedaTipoForm(),
        'form_poblar': PoblarForm(),
    }
    return render(request, 'principal/index.html', contexto)

@require_http_methods(["GET", "POST"])
def buscar_isbn(request):
    resultados, mensaje, tiempo, form = [], "", 0, LibroBusquedaIsbnForm()
    if request.method == 'POST':
        form = LibroBusquedaIsbnForm(request.POST)
        if form.is_valid():
            libro, tiempo = buscar_libro_por_isbn(form.cleaned_data['isbn'])
            resultados = [libro] if libro else []
            mensaje = "" if libro else "No se encontró libro."
    
    return render(request, 'principal/resultados.html', {
        'form': form, 'resultados': resultados, 'mensaje': mensaje,
        'tiempo': tiempo, 'total_tabla': get_cached_book_count(),
        'tipo_busqueda': 'ISBN', 'total_label': 'libros'
    })

@require_http_methods(["GET", "POST"])
def buscar_autor(request):
    resultados, mensaje, tiempo, form = [], "", 0, LibroBusquedaAutorForm()
    if request.method == 'POST':
        form = LibroBusquedaAutorForm(request.POST)
        if form.is_valid():
            # Usamos la función específica
            resultados, tiempo = buscar_por_autor(form.cleaned_data['autor'])
            if not resultados: mensaje = "No se encontraron libros del autor."
    
    return render(request, 'principal/resultados.html', {
        'form': form, 'resultados': resultados, 'mensaje': mensaje,
        'tiempo': tiempo, 'total_tabla': get_cached_book_count(),
        'tipo_busqueda': 'Autor', 'total_label': 'libros'
    })

@require_http_methods(["GET", "POST"])
def buscar_titulo(request):
    resultados, mensaje, tiempo, form = [], "", 0, LibroBusquedaTituloForm()
    if request.method == 'POST':
        form = LibroBusquedaTituloForm(request.POST)
        if form.is_valid():
            # Usamos la función específica para búsqueda de texto
            resultados, tiempo = buscar_libros_por_titulo(form.cleaned_data['titulo'])
            if not resultados: mensaje = "No se encontraron libros con ese título."
            
    return render(request, 'principal/resultados.html', {
        'form': form, 'resultados': resultados, 'mensaje': mensaje,
        'tiempo': tiempo, 'total_tabla': get_cached_book_count(),
        'tipo_busqueda': 'Título', 'total_label': 'libros'
    })

@require_http_methods(["GET", "POST"])
def buscar_usuario_email(request):
    resultados, mensaje, tiempo, form = [], "", 0, UsuarioBusquedaEmailForm()
    if request.method == 'POST':
        form = UsuarioBusquedaEmailForm(request.POST)
        if form.is_valid():
            resultados, tiempo = buscar_usuario_por_email(form.cleaned_data['email'])
            if not resultados: mensaje = "No se encontró usuario con ese email."
            
    return render(request, 'principal/resultados.html', {
        'form': form, 'resultados': resultados, 'mensaje': mensaje,
        'tiempo': tiempo, 'total_tabla': get_cached_user_count(),
        'tipo_busqueda': 'Usuario por Email', 'total_label': 'usuarios'
    })

@require_http_methods(["GET", "POST"])
def registrar_prestamo(request):
    mensaje = ""
    tipo_mensaje = "info"
    
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            # 1. Extraer datos del formulario
            u_id = form.cleaned_data['user_id']
            isbn_libro = form.cleaned_data['isbn']
            
            # 2. Crear el diccionario 'datos_prestamo' que espera la función
            datos_prestamo = {
                'fecha_inicio': str(form.cleaned_data['fecha_inicio']),
                'fecha_fin': str(form.cleaned_data['fecha_fin'])
            }
            
            # 3. Llamada con los 3 parámetros correctos
            resultado_tuple = registrar_prestamo_transaccional(u_id, isbn_libro, datos_prestamo)
            exito = resultado_tuple[0] 
            
            if exito:
                mensaje = f"✅ Préstamo registrado con éxito para el usuario {u_id}"
                tipo_mensaje = "success"
                form = PrestamoForm() 
            else:
                mensaje = "❌ Error en la transacción: El libro podría no estar disponible."
                tipo_mensaje = "danger"
    else:
        form = PrestamoForm()

    return render(request, 'principal/prestamo.html', {
        'form': form,
        'mensaje': mensaje,
        'tipo_mensaje': tipo_mensaje
    })

@require_http_methods(["GET", "POST"])
def buscar_usuario_id(request):
    resultados = []
    mensaje = ""
    tiempo = 0
    form = UsuarioBusquedaIdForm()
    
    if request.method == 'POST':
        form = UsuarioBusquedaIdForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            try:
                # Consulta simple (no requiere batch)
                usuario, tiempo = buscar_usuario_por_id(user_id)
                if usuario:
                    resultados = [usuario]
                else:
                    mensaje = f"No se encontró usuario con ID: {user_id}"
            except Exception as e:
                mensaje = f"Error en la búsqueda: {str(e)}"
    
    total_tabla = get_cached_user_count()
    contexto = {
        'form': form, 'resultados': resultados, 'mensaje': mensaje,
        'tiempo': tiempo, 'total_tabla': total_tabla, 'tipo_busqueda': 'Usuario por ID',
        'total_label': 'usuarios'
    }
    return render(request, 'principal/resultados.html', contexto)

@require_http_methods(["GET", "POST"])
def buscar_usuario_nombre(request):
    resultados = []
    mensaje = ""
    tiempo = 0
    form = UsuarioBusquedaNombreForm()
    
    if request.method == 'POST':
        form = UsuarioBusquedaNombreForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            try:
                # Llamada optimizada
                resultados, tiempo = buscar_por_atributo_batch('Nombre', nombre)
                if not resultados:
                    mensaje = f"No se encontraron usuarios con nombre: {nombre}"
            except Exception as e:
                mensaje = f"Error en la búsqueda: {str(e)}"
    
    total_tabla = get_cached_user_count()
    contexto = {
        'form': form, 'resultados': resultados, 'mensaje': mensaje,
        'tiempo': tiempo, 'total_tabla': total_tabla, 'tipo_busqueda': 'Usuario por Nombre',
        'total_label': 'usuarios'
    }
    return render(request, 'principal/resultados.html', contexto)

@require_http_methods(["GET", "POST"])
def consultar_valoraciones_usuario(request):
    resultados = []
    mensaje = ""
    tiempo = 0
    form = ValoracionesUsuarioForm()
    
    if request.method == 'POST':
        form = ValoracionesUsuarioForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            try:
                # Aquí podrías usar una función similar si fuera necesario, 
                # pero mantenemos la lógica actual si está funcionando bien.
                resultados, tiempo = consultar_valoraciones_por_usuario(user_id)
                if not resultados:
                    mensaje = f"No se encontraron valoraciones para el usuario: {user_id}"
            except Exception as e:
                mensaje = f"Error en la búsqueda: {str(e)}"
    
    total_tabla = get_cached_rating_count()
    contexto = {
        'form': form, 'resultados': resultados, 'mensaje': mensaje,
        'tiempo': tiempo, 'total_tabla': total_tabla, 'tipo_busqueda': 'Valoraciones por Usuario',
        'total_label': 'valoraciones'
    }
    return render(request, 'principal/resultados.html', contexto)

# ... (El resto de funciones como editar_item y poblar_base_datos siguen igual)

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
                resultados, tiempo = buscar_por_tipo_item(tipo_item)
                if not resultados:
                    mensaje = f"No se encontraron items de tipo: {tipo_item}"
            except Exception as e:
                mensaje = f"Error en la búsqueda: {str(e)}"
    
    total_tabla = get_cached_book_count()
    contexto = {
        'form': form,
        'resultados': resultados,
        'mensaje': mensaje,
        'tiempo': tiempo,
        'total_tabla': total_tabla,
        'tipo_busqueda': 'Tipo',
        'total_label': 'libros'
    }
    return render(request, 'principal/resultados.html', contexto)

@require_http_methods(["GET", "POST"])
def editar_item(request):
    mensaje = ""
    item = None
    editable_fields = []

    if request.method == 'GET':
        pk = request.GET.get('pk')
        sk = request.GET.get('sk')
        item = obtener_item(pk, sk) if pk and sk else None
        if not item:
            mensaje = "Item no encontrado para edición."
        else:
            editable_fields = [
                campo for campo in item.keys()
                if campo not in ('PK', 'SK', 'EntityType') and not isinstance(item[campo], (list, dict))
            ]

    if request.method == 'POST':
        pk = request.POST.get('pk')
        sk = request.POST.get('sk')
        item = obtener_item(pk, sk) if pk and sk else None
        if not item:
            mensaje = "Item no encontrado para edición."
        else:
            atributos = {}
            for campo, valor in request.POST.items():
                if campo in ('csrfmiddlewaretoken', 'pk', 'sk'):
                    continue
                if valor is None:
                    continue
                valor = valor.strip()
                if valor == '':
                    continue
                if campo in ('Paginas', 'DuracionMinutos', 'Puntuacion'):
                    try:
                        valor = int(valor)
                    except ValueError:
                        pass
                atributos[campo] = valor
            actualizado = actualizar_item(pk, sk, atributos)
            if actualizado is not None:
                mensaje = 'Los datos se actualizaron correctamente.'
                item = actualizado
            else:
                mensaje = 'No se realizó ningún cambio.'
            editable_fields = [
                campo for campo in item.keys()
                if campo not in ('PK', 'SK', 'EntityType') and not isinstance(item[campo], (list, dict))
            ]

    contexto = {
        'item': item,
        'field_list': [{'campo': c, 'valor': item.get(c, '')} for c in editable_fields],
        'mensaje': mensaje,
    }
    return render(request, 'principal/editar.html', contexto)

@require_http_methods(["GET", "POST"])
def poblar_base_datos(request):
    """Vista para poblar la base de datos con libros, usuarios y autores aleatorios."""
    mensaje = ""
    form = PoblarForm()
    
    if request.method == 'POST':
        form = PoblarForm(request.POST)
        if form.is_valid():
            try:
                num_libros = form.cleaned_data['num_libros']
                num_usuarios = form.cleaned_data['num_usuarios']
                num_autores = form.cleaned_data['num_autores']
                
                poblar_todo(num_libros, num_usuarios, num_autores)
                mensaje = f"¡Éxito! Se han creado {num_libros} libros, {num_usuarios} usuarios y {num_autores} autores."
                form = PoblarForm()
            except Exception as e:
                mensaje = f"Error al poblar la base de datos: {str(e)}"
    
    contexto = {
        'mensaje': mensaje,
        'form': form,
    }
    return render(request, 'principal/poblar.html', contexto)