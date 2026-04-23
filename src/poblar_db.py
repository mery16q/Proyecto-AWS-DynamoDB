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

def poblar_todo():
    print("--- 🚀 INICIANDO POBLADO DE SISTEMA COMPLETO ---")
    vaciar_tabla()
    
    num_libros = 50
    num_usuarios = 10
    num_autores = 5
    
    with table.batch_writer() as batch:
        # 1. Crear Autores
        lista_autores = [fake.unique.name() for _ in range(num_autores)]
        for nombre in lista_autores:
            batch.put_item(Item={
                'PK': f'AUTHOR#{nombre.replace(" ", "_").upper()}',
                'SK': 'METADATOS',
                'EntityType': 'AUTOR',
                'Nombre': nombre,
                'Biografia': "Escritor destacado del catálogo."
            })
        
        # 2. Crear Usuarios
        lista_uids = [f"USER{i}" for i in range(1, num_usuarios + 1)]
        for uid in lista_uids:
            batch.put_item(Item={
                'PK': f'USER#{uid}',
                'SK': 'PROFILE',
                'EntityType': 'USUARIO',
                'Nombre': fake.unique.name(),
                'Email': fake.unique.email()
            })
            
        # 3. Crear Libros y sus Valoraciones
        lista_isbns = []
        for _ in range(num_libros):
            isbn = fake.unique.isbn13()
            lista_isbns.append(isbn)
            
            # Insertar Libro
            batch.put_item(Item=generar_datos_libro(isbn))
            
            # Valoraciones (1 a 3 por libro) con usuarios únicos por libro
            usuarios_valoracion = random.sample(lista_uids, k=random.randint(1, min(3, len(lista_uids))))
            for uid in usuarios_valoracion:
                batch.put_item(Item={
                    'PK': f'LIBRO#{isbn}',
                    'SK': f'RATING#{uid}',
                    'EntityType': 'VALORACION',
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
            batch.put_item(Item={
                'PK': f'USER#{random.choice(lista_uids)}',
                'SK': f'LOAN#{loan_id}',
                'EntityType': 'PRESTAMO',
                'ISBN_Libro': f'LIBRO#{random.choice(lista_isbns)}',
                'Estado': 'ACTIVO'
            })

    print("✅ Datos inyectados correctamente.")

if __name__ == "__main__":
    poblar_todo()