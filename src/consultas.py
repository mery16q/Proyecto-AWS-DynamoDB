import os
import boto3
import time
from boto3.dynamodb.conditions import Key, Attr
from dotenv import load_dotenv

load_dotenv()

# Configuración
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
table = dynamodb.Table('CatalogoLibros')

def medir_rendimiento(func):
    """Decorador para devolver el resultado y el tiempo de ejecución."""
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        fin = time.perf_counter()
        latencia = (fin - inicio) * 1000  # En milisegundos
        print(f"⏱️ Consulta [{func.__name__}]: {latencia:.2f} ms")
        return resultado, round(latencia, 2)
    return wrapper

# --- BÚSQUEDAS DE LIBROS ---

@medir_rendimiento
def buscar_libro_por_isbn(isbn):
    """Búsqueda directa por Clave Primaria (PK)."""
    respuesta = table.get_item(
        Key={'PK': f'LIBRO#{isbn}', 'SK': 'METADATOS'}
    )
    return respuesta.get('Item')

@medir_rendimiento
def buscar_libros_por_titulo(titulo):
    """Búsqueda de libros por título (Scan con filtro)."""
    respuesta = table.scan(
        FilterExpression=Attr('EntityType').eq('LIBRO') & Attr('Titulo').contains(titulo)
    )
    return respuesta.get('Items', [])

@medir_rendimiento
def buscar_por_autor(autor):
    """Búsqueda por autor usando GSI (Eficiente)."""
    respuesta = table.query(
        IndexName='AutorIndex',
        KeyConditionExpression=Key('Autor').eq(autor)
    )
    return respuesta.get('Items', [])


# --- BÚSQUEDAS DE USUARIOS ---

@medir_rendimiento
def buscar_usuario_por_id(user_id):
    """Busca un usuario específico por su ID de perfil."""
    respuesta = table.get_item(
        Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'}
    )
    return respuesta.get('Item')

@medir_rendimiento
def buscar_usuario_por_email(email):
    """Busca usuarios por email (Scan con filtro)."""
    respuesta = table.scan(
        FilterExpression=Attr('EntityType').eq('USUARIO') & Attr('Email').eq(email)
    )
    return respuesta.get('Items', [])

@medir_rendimiento
def buscar_usuario_por_nombre(nombre):
    """Busca usuarios por nombre (Scan con filtro)."""
    respuesta = table.scan(
        FilterExpression=Attr('EntityType').eq('USUARIO') & Attr('Nombre').contains(nombre)
    )
    return respuesta.get('Items', [])

# --- BÚSQUEDA DE VALORACIONES ---

@medir_rendimiento
def consultar_valoraciones_por_usuario(user_id):
    """
    Busca todas las valoraciones realizadas por un usuario específico.
    Como las valoraciones tienen SK 'RATING#USERID', usamos Scan con filtro en SK.
    """
    respuesta = table.scan(
        FilterExpression=Attr('EntityType').eq('VALORACION') & Attr('SK').eq(f'RATING#USER#{user_id}')
    )
    return respuesta.get('Items', [])

# --- UTILIDADES ---

@medir_rendimiento
def scan_por_tipo_item(tipo_item):
    """Búsqueda por tipo de ítem (Scan con filtro)."""
    respuesta = table.scan(
        FilterExpression=Attr('EntityType').eq('LIBRO') & Attr('TipoItem').eq(tipo_item)
    )
    return respuesta.get('Items', [])


def obtener_item(pk, sk):
    """Obtiene un item genérico por PK y SK."""
    respuesta = table.get_item(Key={'PK': pk, 'SK': sk})
    return respuesta.get('Item')


def actualizar_item(pk, sk, atributos):
    """Actualiza atributos no clave de un item."""
    if not atributos:
        return None

    update_expression = 'SET ' + ', '.join(f"#{campo} = :{campo}" for campo in atributos)
    expression_attribute_names = {f"#{campo}": campo for campo in atributos}
    expression_attribute_values = {f":{campo}": valor for campo, valor in atributos.items()}

    respuesta = table.update_item(
        Key={'PK': pk, 'SK': sk},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues='ALL_NEW'
    )
    return respuesta.get('Attributes')


def obtener_tamano_tabla():
    """Devuelve el número total de ítems reales en la tabla."""
    respuesta = table.scan(Select='COUNT')
    return respuesta.get('Count', 0)