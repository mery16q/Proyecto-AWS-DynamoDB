import os
import random
import boto3
from faker import Faker
from dotenv import load_dotenv

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

def poblar_tabla(total_registros=10000):
    print(f"Iniciando carga masiva de {total_registros} registros...")
    
    fake.unique.clear()
    try:
        # El batch_writer gestiona automáticamente el buffering y reintentos
        with table.batch_writer() as batch:
            for i in range(total_registros):
                isbn = fake.unique.isbn13()
                batch.put_item(Item=generar_datos_libro(isbn))
                
                if (i + 1) % 1000 == 0:
                    print(f"Progreso: {i + 1} registros insertados.")
                    
        print("¡Éxito! Base de datos poblada correctamente.")
        
    except Exception as e:
        print(f"Error durante la carga: {e}")

if __name__ == "__main__":
    poblar_tabla(10000)