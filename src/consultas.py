import os
import boto3
import time
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
client = dynamodb.meta.client
table = dynamodb.Table('CatalogoLibros')

def medir_rendimiento(func):
    """Decorador para devolver el resultado y el tiempo de ejecución."""
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        fin = time.perf_counter()
        print(f"[{func.__name__}]: {(fin - inicio)*1000:.2f} ms")
        return resultado, round((fin - inicio)*1000, 2)
    return wrapper

def obtener_metadatos_en_batch(lista_de_claves):
    if not lista_de_claves: return []
    respuesta = dynamodb.batch_get_item(RequestItems={'CatalogoLibros': {'Keys': lista_de_claves}})
    return respuesta['Responses'].get('CatalogoLibros', [])

@medir_rendimiento
def registrar_prestamo_transaccional(user_id, isbn, datos_prestamo):
    f_ini_nueva = datos_prestamo['fecha_inicio']
    f_fin_nueva = datos_prestamo['fecha_fin']

    # PASO 1: Consultar todos los préstamos ACTIVOS de ese libro en el GSI
    try:
        respuesta = table.query(
            IndexName='GSI_ByAttribute',
            KeyConditionExpression=Key('AttributeName').eq('ISBN_PRESTAMO') & 
                                   Key('AttributeValue').eq(f'LIBRO#{isbn}')
        )
        prestamos_del_libro = respuesta.get('Items', [])

        # PASO 2: Algoritmo de detección de solapamiento
        for p in prestamos_del_libro:
            if p.get('Estado') == 'ACTIVO':
                f_ini_ex = p['FechaInicio']
                f_fin_ex = p['FechaFin']
                
                if f_ini_nueva <= f_fin_ex and f_fin_nueva >= f_ini_ex:
                    print(f"❌ Conflicto: El libro ya está reservado del {f_ini_ex} al {f_fin_ex}")
                    return False

    except ClientError as e:
        print(f"Error consultando GSI: {e}")
        return False

    # PASO 3: Transacción Atómica
    try:
        timestamp = int(time.time())
        client.transact_write_items(TransactItems=[
            {
                'Put': {
                    'TableName': 'CatalogoLibros',
                    'Item': {
                        'PK': f'USER#{user_id}',
                        'SK': f'PRESTAMO#{isbn}#{timestamp}',
                        'EntityType': 'PRESTAMO',
                        'AttributeName': 'ISBN_PRESTAMO',
                        'AttributeValue': f'LIBRO#{isbn}',
                        'ISBN_Libro': isbn,
                        'FechaInicio': f_ini_nueva,
                        'FechaFin': f_fin_nueva,
                        'Estado': 'ACTIVO'
                    }
                }
            },
            {
                'Update': {
                    'TableName': 'CatalogoLibros',
                    'Key': {'PK': f'LIBRO#{isbn}', 'SK': 'METADATOS'},
                    'UpdateExpression': 'SET #est = :nuevo',
                    'ExpressionAttributeNames': {'#est': 'Estado'},
                    'ExpressionAttributeValues': {':nuevo': 'PRESTADO'}
                }
            }
        ])
        return True
    except ClientError as e:
        print(f"Error en transacción: {e}")
        return False

@medir_rendimiento
def buscar_por_atributo_batch(attr_name, value):
    resp = table.query(IndexName='GSI_ByAttribute', KeyConditionExpression=Key('AttributeName').eq(attr_name) & Key('AttributeValue').eq(value))
    items = resp.get('Items', [])
    if not items: return []
    return obtener_metadatos_en_batch([{'PK': i['PK'], 'SK': i['SK']} for i in items])

@medir_rendimiento
def buscar_libro_por_isbn(isbn):
    """Búsqueda directa por Clave Primaria (PK)."""
    respuesta = table.get_item(
        Key={'PK': f'LIBRO#{isbn}', 'SK': 'METADATOS'}
    )
    return respuesta.get('Item')

@medir_rendimiento
def buscar_libros_por_titulo(titulo):
    respuesta = table.query(
        IndexName='GSI_ByAttribute',
        KeyConditionExpression=Key('AttributeName').eq('Titulo') & 
                               Key('AttributeValue').begins_with(titulo)
    )
    items = respuesta.get('Items', [])
    if not items:
        return []
    pk = items[0]['PK']
    resultado = table.query(KeyConditionExpression=Key('PK').eq(pk))
    return resultado.get('Items', [])

@medir_rendimiento
def buscar_por_autor(autor):
    respuesta = table.query(
        IndexName='GSI_ByAttribute',
        KeyConditionExpression=Key('AttributeName').eq('Autor') & 
                               Key('AttributeValue').eq(autor)
    )
    items = respuesta.get('Items', [])
    if not items:
        return []
    pk = items[0]['PK']
    resultado = table.query(KeyConditionExpression=Key('PK').eq(pk))
    return resultado.get('Items', [])

@medir_rendimiento
def buscar_usuario_por_id(user_id):
    """Busca un usuario específico por su ID de perfil."""
    respuesta = table.get_item(
        Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'}
    )
    return respuesta.get('Item')


#PK: USUARIO

@medir_rendimiento
def buscar_usuario_por_email(email):
    # Paso 1: buscar el puntero en el GSI
    respuesta = table.query(
        IndexName='GSI_ByAttribute',
        KeyConditionExpression=Key('AttributeName').eq('Email') & 
                               Key('AttributeValue').eq(email)
    )
    items = respuesta.get('Items', [])
    if not items:
        return []
    
    # Paso 2: con la PK encontrada, traer todos los ítems del usuario
    pk = items[0]['PK']  # ej: USER#8
    resultado = table.query(
        KeyConditionExpression=Key('PK').eq(pk)
    )
    return resultado.get('Items', [])

#VALORACIONES

@medir_rendimiento
def consultar_valoraciones_por_usuario(user_id):
    """
    Busca todas las valoraciones de un usuario usando el GSI.
    """
    resp = table.query(
        IndexName='GSI_User_Ratings',
        KeyConditionExpression=Key('UserID').eq(f'USER#{user_id}')
    )
    return resp.get('Items', [])

@medir_rendimiento
def consultar_prestamos_por_usuario(user_id):
    """
    Busca todos los préstamos de un usuario usando la clave primaria del usuario.
    """
    resp = table.query(
        KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & 
                               Key('SK').begins_with('PRESTAMO#')
    )
    return resp.get('Items', [])

def obtener_total_prestamos():
    return obtener_total_entidad('PRESTAMO')

@medir_rendimiento
def buscar_por_tipo_item(tipo):
    respuesta = table.query(
        IndexName='GSI_ByAttribute',
        KeyConditionExpression=Key('AttributeName').eq('TipoItem') & 
                               Key('AttributeValue').eq(tipo)
    )
    items = respuesta.get('Items', [])
    if not items:
        return []
    # Aquí puede haber MÚLTIPLES libros, no solo uno
    claves = [{'PK': i['PK'], 'SK': 'METADATOS'} for i in items if i['SK'] == 'TipoItem']
    return obtener_metadatos_en_batch(claves)

def obtener_item(pk, sk):
    """
    Esta función estaba perfecta. Búsqueda directa y barata.
    """
    return table.get_item(
        Key={'PK': pk, 'SK': sk}
    ).get('Item')

def actualizar_item(pk, sk, atributos):
    """
    Actualiza el ítem y te lo devuelve actualizado en una sola petición.
    """
    update_expr = "SET " + ", ".join([f"#{k} = :{k}" for k in atributos.keys()])
    expr_names = {f"#{k}": k for k in atributos.keys()}
    expr_vals = {f":{k}": v for k, v in atributos.items()}
    
    resp = table.update_item(
        Key={'PK': pk, 'SK': sk}, 
        UpdateExpression=update_expr, 
        ExpressionAttributeNames=expr_names, 
        ExpressionAttributeValues=expr_vals,
        ReturnValues='ALL_NEW' 
    )
    return resp.get('Attributes')

def obtener_tamano_tabla():
    """
    Obtiene el total de registros casi al instante y GRATIS.
    Nota: Se actualiza cada ~6 horas, por lo que es un aproximado,
    pero es el estándar de la industria frente al costosísimo Scan.
    """
    resp = client.describe_table(TableName='CatalogoLibros')
    return resp['Table'].get('ItemCount', 0)


def obtener_total_entidad(entity_type):
    """
    Cuenta los ítems principales por tipo de entidad (LIBRO, USUARIO, VALORACION).
    Usa scan con Select='COUNT' y paginación para calcular solo el total.
    """
    total = 0
    exclusive_start_key = None
    filtro = Attr('EntityType').eq(entity_type)

    while True:
        scan_kwargs = {'Select': 'COUNT', 'FilterExpression': filtro}
        if exclusive_start_key:
            scan_kwargs['ExclusiveStartKey'] = exclusive_start_key

        resp = table.scan(**scan_kwargs)
        total += resp.get('Count', 0)
        exclusive_start_key = resp.get('LastEvaluatedKey')

        if not exclusive_start_key:
            break

    return total


def obtener_total_libros():
    return obtener_total_entidad('LIBRO')


def obtener_total_usuarios():
    return obtener_total_entidad('USUARIO')


def obtener_total_valoraciones():
    return obtener_total_entidad('VALORACION')