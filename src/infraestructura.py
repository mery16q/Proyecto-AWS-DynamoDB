import os
import boto3
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def crear_tabla():
    print("Creando tabla 'CatalogoLibros'...")
    try:
        tabla = dynamodb.create_table(
            TableName='CatalogoLibros',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'Autor', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'AutorIndex',
                    'KeySchema': [
                        {'AttributeName': 'Autor', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST' 
        )
        print("Tabla creada. Esperando a que esté lista...")
        tabla.wait_until_exists()
        print("¡Tabla lista para usar!")
    except Exception as e:
        print(f"Error al crear: {e}")

if __name__ == "__main__":
    crear_tabla()