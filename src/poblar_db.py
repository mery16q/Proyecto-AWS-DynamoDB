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

def poblar_todo():
    print("--- INICIANDO CARGA TOTAL (Libros, Usuarios, Préstamos, Autores, Valoraciones) ---")
    
    # Datos de control
    lista_libros = []
    lista_usuarios = [f"USER{i}" for i in range(1, 11)]
    lista_autores = [fake.name() for _ in range(5)]

    with table.batch_writer() as batch:
        # 1. Crear Autores (Entidad Independiente)
        for autor in lista_autores:
            slug = autor.replace(" ", "_").upper()
            batch.put_item(Item={
                'PK': f'AUTHOR#{slug}',
                'SK': 'METADATOS',
                'Nombre': autor,
                'Biografia': fake.text(max_nb_chars=100)
            })
        print("✅ Autores creados.")

        # 2. Crear Usuarios
        for uid in lista_usuarios:
            batch.put_item(Item={
                'PK': f'USER#{uid}',
                'SK': 'PROFILE',
                'Nombre': fake.name(),
                'Email': fake.email()
            })
        print("✅ Usuarios creados.")

        # 3. Crear Libros
        for _ in range(30):
            isbn = fake.unique.isbn13()
            autor_aleatorio = random.choice(lista_autores)
            lista_libros.append(isbn)
            
            batch.put_item(Item={
                'PK': f'LIBRO#{isbn}',
                'SK': 'METADATOS',
                'Titulo': fake.sentence(nb_words=3),
                'Autor': autor_aleatorio
            })

            # 4. Crear Valoraciones (Vinculadas al Libro - Adjacency List)
            # Creamos 1-3 valoraciones por cada libro
            for _ in range(random.randint(1, 3)):
                user_rater = random.choice(lista_usuarios)
                batch.put_item(Item={
                    'PK': f'LIBRO#{isbn}',
                    'SK': f'RATING#{user_rater}', # SK identifica al usuario que vota
                    'Puntuacion': random.randint(1, 5),
                    'Comentario': fake.sentence()
                })
        print("✅ Libros y Valoraciones creados.")

        # 5. Crear Préstamos (Vinculados al Usuario)
        for _ in range(20):
            uid = random.choice(lista_usuarios)
            isbn = random.choice(lista_libros)
            batch.put_item(Item={
                'PK': f'USER#{uid}',
                'SK': f'LOAN#{uuid.uuid4().hex[:6]}',
                'ISBN_Libro': f'LIBRO#{isbn}',
                'Estado': 'ACTIVO'
            })
        print("✅ Préstamos creados.")

    print("--- PROCESO FINALIZADO CON ÉXITO ---")

if __name__ == "__main__":
    poblar_todo()