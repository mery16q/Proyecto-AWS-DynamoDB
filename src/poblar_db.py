import os
import random
import uuid
import boto3
from faker import Faker
from dotenv import load_dotenv

load_dotenv()

fake = Faker()
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
table = dynamodb.Table('CatalogoLibros')

def vaciar_tabla():
    """Vacía completamente la tabla DynamoDB."""
    print("🧹 Vaciando la tabla...")
    response = table.scan(ProjectionExpression='PK, SK')
    items = response.get('Items', [])
    
    while 'LastEvaluatedKey' in response:
        response = table.scan(ProjectionExpression='PK, SK', ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    
    if items:
        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={'PK': item['PK'], 'SK': item['SK']})
        print(f"✅ Eliminados {len(items)} ítems.")
    else:
        print("La tabla ya estaba vacía.")

def generar_datos_libro(isbn):
    """Genera datos de un libro con su EntityType."""
    tipo_formato = random.choice(['FISICO', 'EBOOK', 'AUDIO'])
    item = {
        'PK': f'LIBRO#{isbn}',
        'SK': 'METADATOS',
        'EntityType': 'LIBRO',
        'TipoItem': tipo_formato,
        'Titulo': fake.sentence(nb_words=3).replace('.', ''),
        'Autor': fake.name()
    }
    if tipo_formato == 'EBOOK': 
        item['Formato'] = random.choice(['PDF', 'EPUB'])
    elif tipo_formato == 'AUDIO': 
        item['DuracionMinutos'] = random.randint(60, 900)
        item['Narrador'] = fake.name()
    else: 
        item['Paginas'] = random.randint(50, 1000)
    return item

def poblar_todo(num_libros=50, num_usuarios=10, num_autores=5):
    print("--- 🚀 INICIANDO POBLADO DE SISTEMA COMPLETO ---")
    vaciar_tabla()
    
    GENEROS = ['Ficción', 'No ficción', 'Ciencia ficción', 'Fantasía', 'Misterio', 'Romance', 'Historia', 'Biografía']

    with table.batch_writer() as batch:

        # 1. Crear Autores
        lista_autores = [fake.unique.name() for _ in range(num_autores)]
        for nombre in lista_autores:
            pk = f'AUTHOR#{nombre.replace(" ", "_").upper()}'
            batch.put_item(Item={
                'PK': pk,
                'SK': 'METADATOS',
                'EntityType': 'AUTOR',
                'Nombre': nombre,
                'Biografia': fake.sentence()
            })
            # Puntero GSI por Nombre
            batch.put_item(Item={
                'PK': pk,
                'SK': 'Nombre',
                'AttributeName': 'Nombre',
                'AttributeValue': nombre
            })

        # 2. Crear Usuarios
        lista_uids = [f"{i}" for i in range(1, num_usuarios + 1)]
        for uid in lista_uids:
            nombre_usuario = fake.unique.name()
            email_usuario  = fake.unique.email()
            pk = f'USER#{uid}'

            batch.put_item(Item={
                'PK': pk,
                'SK': 'PROFILE',
                'EntityType': 'USUARIO',
                'Nombre': nombre_usuario,
                'Email': email_usuario
            })
            # Punteros GSI
            batch.put_item(Item={
                'PK': pk, 'SK': 'Email',
                'AttributeName': 'Email',
                'AttributeValue': email_usuario
            })
            batch.put_item(Item={
                'PK': pk, 'SK': 'Nombre',
                'AttributeName': 'Nombre',
                'AttributeValue': nombre_usuario
            })

        # 3. Crear Libros y Valoraciones
        lista_isbns = []
        for _ in range(num_libros):
            isbn  = fake.unique.isbn13()
            lista_isbns.append(isbn)
            pk    = f'LIBRO#{isbn}'
            autor = fake.name()
            titulo = fake.sentence(nb_words=3).replace('.', '')
            genero = random.choice(GENEROS)
            anio   = str(random.randint(1950, 2024))
            tipo   = random.choice(['FISICO', 'EBOOK', 'AUDIO'])

            # Item principal
            item = {
                'PK': pk,
                'SK': 'METADATOS',
                'EntityType': 'LIBRO',
                'ISBN': isbn,
                'Titulo': titulo,
                'Autor': autor,
                'Genero': genero,
                'Anio': anio,
                'TipoItem': tipo,
            }
            if tipo == 'EBOOK':
                item['Formato'] = random.choice(['PDF', 'EPUB'])
                item['TamanoArchivo'] = f"{random.randint(1, 50)}MB"
            elif tipo == 'AUDIO':
                item['DuracionMinutos'] = random.randint(60, 900)
                item['Narrador'] = fake.name()
            else:
                item['Paginas'] = random.randint(50, 1000)

            batch.put_item(Item=item)

            # Punteros GSI
            for attr_name, attr_value in [
                ('Titulo',   titulo),
                ('Autor',    autor),
                ('Genero',   genero),
                ('TipoItem', tipo),
            ]:
                batch.put_item(Item={
                    'PK': pk,
                    'SK': attr_name,
                    'AttributeName': attr_name,
                    'AttributeValue': attr_value
                })

            # Valoraciones
            usuarios_valoracion = random.sample(lista_uids, k=random.randint(1, min(3, len(lista_uids))))
            for uid in usuarios_valoracion:
                batch.put_item(Item={
                    'PK': pk,
                    'SK': f'RATING#{uid}',
                    'EntityType': 'VALORACION',
                    'UserID': f'USER#{uid}',
                    'Fecha': fake.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%dT%H:%M:%S'),  # ← aquí
                    'Puntuacion': random.randint(1, 5),
                    'Comentario': fake.sentence()
                })

        # 4. Crear Préstamos
        used_loan_ids = set()
        while len(used_loan_ids) < 30:
            loan_id = uuid.uuid4().hex
            if loan_id in used_loan_ids:
                continue
            used_loan_ids.add(loan_id)
            fecha_prestamo   = fake.date_between(start_date='-1y', end_date='today')
            fecha_devolucion = fake.date_between(start_date=fecha_prestamo, end_date='+30d')
            random_isbn = random.choice(lista_isbns)
            batch.put_item(Item={
                'PK': f'USER#{random.choice(lista_uids)}',
                'SK': f'PRESTAMO#{loan_id}',
                'EntityType': 'PRESTAMO',
                'ISBN_Libro': random_isbn,
                'AttributeName': 'ISBN_PRESTAMO',
                'AttributeValue': f'LIBRO#{random_isbn}',                
                'Estado': 'ACTIVO',
                'FechaPrestamo':   str(fecha_prestamo),
                'FechaDevolucion': str(fecha_devolucion),
            })

    print("✅ Datos inyectados correctamente.")
    
if __name__ == "__main__":
    poblar_todo()