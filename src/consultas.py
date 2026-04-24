import os
import boto3
import time
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

# Configuración
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
client = dynamodb.meta.client
table = dynamodb.Table('CatalogoLibros')

# --- DECORADOR ---
def medir_rendimiento(func):
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        fin = time.perf_counter()
        print(f"⏱️ [{func.__name__}]: {(fin - inicio)*1000:.2f} ms")
        return resultado, round((fin - inicio)*1000, 2)
    return wrapper

# --- LÓGICA DE DATOS ---

def obtener_metadatos_en_batch(lista_de_claves):
    if not lista_de_claves: return []
    respuesta = dynamodb.batch_get_item(RequestItems={'CatalogoLibros': {'Keys': lista_de_claves}})
    return respuesta['Responses'].get('CatalogoLibros', [])

@medir_rendimiento
def registrar_prestamo_transaccional(user_id, isbn, datos_prestamo):
    # 1. Calcula el tiempo ANTES de intentar la transacción
    # (30 días en el futuro)
    tiempo_expiracion = int(time.time()) + (30 * 24 * 60 * 60)
    
    try:
        client.transact_write_items(TransactItems=[
            {
                'Put': {
                    'TableName': 'CatalogoLibros', 
                    'Item': {
                        'PK': f'USER#{user_id}', 
                        'SK': f'PRESTAMO#{isbn}', 
                        'EntityType': 'PRESTAMO', 
                        'FechaInicio': datos_prestamo['fecha_inicio'], 
                        'FechaFin': datos_prestamo['fecha_fin'], 
                        'Estado': 'ACTIVO',
                        # <--- AQUÍ ES DONDE LO TIENES QUE PONER:
                        'ttl_expiration': {'N': str(tiempo_expiracion)}
                    }
                }
            },
            {
                'Update': {
                    'TableName': 'CatalogoLibros', 
                    'Key': {'PK': f'LIBRO#{isbn}', 'SK': 'METADATOS'}, 
                    'UpdateExpression': 'SET #est = :nuevo', 
                    'ConditionExpression': '#est = :disp', 
                    'ExpressionAttributeNames': {'#est': 'Estado'}, 
                    'ExpressionAttributeValues': {':nuevo': 'PRESTADO', ':disp': 'DISPONIBLE'}
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
    return table.get_item(Key={'PK': f'LIBRO#{isbn}', 'SK': 'METADATOS'}).get('Item')

@medir_rendimiento
def buscar_usuario_por_id(user_id):
    return table.get_item(Key={'PK': f'USER#{user_id}', 'SK': 'METADATOS'}).get('Item')

@medir_rendimiento
def buscar_usuario_por_email(email):
    return buscar_por_atributo_batch('Email', email)[0] # Simplificado para el ejemplo

@medir_rendimiento
def buscar_usuario_por_nombre(nombre):
    return buscar_por_atributo_batch('Nombre', nombre)[0]

@medir_rendimiento
def buscar_libros_por_titulo(titulo):
    return buscar_por_atributo_batch('Titulo', titulo)[0]

@medir_rendimiento
def buscar_por_autor(autor):
    return buscar_por_atributo_batch('Autor', autor)[0]

@medir_rendimiento
def consultar_valoraciones_por_usuario(user_id):
    return table.query(KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & Key('SK').begins_with('VALORACION#')).get('Items', [])

@medir_rendimiento
def scan_por_tipo_item(tipo):
    resp = table.scan(FilterExpression=Attr('EntityType').eq(tipo))
    return resp.get('Items', [])

@medir_rendimiento
def obtener_item(pk, sk):
    return table.get_item(Key={'PK': pk, 'SK': sk}).get('Item')

@medir_rendimiento
def actualizar_item(pk, sk, atributos):
    update_expr = "SET " + ", ".join([f"#{k} = :{k}" for k in atributos.keys()])
    expr_names = {f"#{k}": k for k in atributos.keys()}
    expr_vals = {f":{k}": v for k, v in atributos.items()}
    table.update_item(Key={'PK': pk, 'SK': sk}, UpdateExpression=update_expr, ExpressionAttributeNames=expr_names, ExpressionAttributeValues=expr_vals)
    return obtener_item(pk, sk)

@medir_rendimiento
def obtener_tamano_tabla():
    return table.scan(Select='COUNT').get('Count', 0)