import os
import random
import boto3
from faker import Faker
from dotenv import load_dotenv
from consultas import obtener_tamano_tabla

load_dotenv()

# Inicializamos Faker y el cliente de DynamoDB
fake = Faker()
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
table = dynamodb.Table('CatalogoLibros')

def generar_datos_libro(isbn):
    """Genera un diccionario con datos realistas siguiendo Single-Table Design."""
    tipo_formato = random.choice(['FISICO', 'EBOOK', 'AUDIO'])
    
    # Atributos comunes
    item = {
        'PK': f'LIBRO#{isbn}',
        'SK': 'METADATOS',
        'TipoItem': tipo_formato,
        'Titulo': fake.sentence(nb_words=4).replace('.', ''),
        'Autor': fake.name()
    }

    # Atributos específicos según formato (Esquema Flexible)
    if tipo_formato == 'EBOOK':
        item['Formato'] = random.choice(['PDF', 'EPUB'])
    elif tipo_formato == 'AUDIO':
        item['DuracionMinutos'] = random.randint(60, 900)
        item['Narrador'] = fake.name()
    else:  # FISICO
        item['Paginas'] = random.randint(50, 1000)

    return item

def vaciar_tabla():
    """Vacía completamente la tabla DynamoDB eliminando todos los ítems."""
    print("Vaciando la tabla existente...")
    try:
        # Scan para obtener todas las claves primarias
        response = table.scan(ProjectionExpression='PK, SK')
        items_to_delete = response.get('Items', [])
        
        # Manejar paginación si hay muchos ítems
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                ProjectionExpression='PK, SK',
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items_to_delete.extend(response.get('Items', []))
        
        if not items_to_delete:
            print("La tabla ya está vacía.")
            return
        
        # Eliminar en batch
        with table.batch_writer() as batch:
            for item in items_to_delete:
                batch.delete_item(Key={'PK': item['PK'], 'SK': item['SK']})
        
        print(f"Eliminados {len(items_to_delete)} ítems existentes.")
        
    except Exception as e:
        print(f"Error al vaciar la tabla: {e}")
        raise

def poblar_tabla(objetivo=10000):
    print(f"--- INICIANDO CARGA DE DATOS PRECISA ---")
    vaciar_tabla()
    
    actuales = obtener_tamano_tabla()

    intentos_totales = 0
    max_intentos_globales = objetivo * 2 # Evita bucles infinitos si hay errores graves

    # 2. Bucle de control basado en el estado real de la base de datos
    while actuales < objetivo and intentos_totales < max_intentos_globales:
        faltantes = objetivo - actuales
        print(f"Progreso: {actuales}/{objetivo}. Insertando bloque de {faltantes} faltantes...")
        
        try:
            # El batch_writer es eficiente pero no garantiza que todos los items entren si hay duplicados
            with table.batch_writer() as batch:
                for _ in range(faltantes):
                    # Usamos unique.isbn13 para minimizar colisiones en la misma sesión
                    isbn = fake.unique.isbn13() 
                    item = generar_datos_libro(isbn)
                    batch.put_item(Item=item)
                    intentos_totales += 1
            
            # Limpiamos la memoria de 'unique' tras cada bloque para evitar saturación
            fake.unique.clear()
            
        except Exception as e:
            print(f"Error durante la inserción del bloque: {e}")
        
        # 3. Verificación CRÍTICA: Consultamos el cardinal real de la tabla
        actuales = obtener_tamano_tabla() 
        print(f"Conteo real tras validación de base de datos: {actuales}")

    if actuales == objetivo:
        print(f"¡Éxito! La tabla tiene exactamente {actuales} registros únicos.")
    else:
        print(f"Finalizado. Registros finales: {actuales}. Revisa posibles colisiones externas.")

if __name__ == "__main__":
    poblar_tabla(10000)