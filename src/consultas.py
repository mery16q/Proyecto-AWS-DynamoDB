import os
import boto3
import time
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
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

@medir_rendimiento
def buscar_libro_por_isbn(isbn):
    """Búsqueda directa por Clave Primaria (La más rápida)."""
    respuesta = table.get_item(
        Key={
            'PK': f'LIBRO#{isbn}',
            'SK': 'METADATOS'
        }
    )
    return respuesta.get('Item')

@medir_rendimiento
def buscar_por_autor(autor):
    """
    Búsqueda por autor usando el Índice Secundario Global (GSI) 'AutorIndex'.
    """
    respuesta = table.query(
        IndexName='AutorIndex',
        KeyConditionExpression=Key('Autor').eq(autor)
    )
    return respuesta.get('Items')

@medir_rendimiento
def scan_por_tipo_item(tipo_item):
    """
    Búsqueda por tipo de ítem usando scan.
    Filtra por el atributo 'TipoItem' (FISICO, EBOOK, AUDIO).
    """
    respuesta = table.scan(
        FilterExpression=Attr('TipoItem').eq(tipo_item)
    )
    return respuesta.get('Items')


def obtener_tamano_tabla():
    """Devuelve el número total de ítems en la tabla DynamoDB."""
    try:
        table.load()
        if table.item_count is not None:
            return int(table.item_count)
    except Exception:
        pass

    respuesta = table.scan(Select='COUNT')
    return respuesta.get('Count', 0)

# --- EJEMPLO DE PRUEBA ---
if __name__ == "__main__":
    print("--- INICIANDO PRUEBAS DE RENDIMIENTO ---")
    
    # 1. Prueba de GetItem (Reemplaza con un ISBN real de tu tabla)
    # libro = buscar_libro_por_isbn('9781234567890')
    
    # 2. Prueba de Scan por Autor
    # libros_autor = buscar_por_autor('Nombre de Autor Inventado')
    
    # 3. Prueba de Scan por Tipo de Ítem
    # resultados = scan_por_tipo_item('FISICO')