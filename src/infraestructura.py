import boto3
import os
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def crear_tabla():
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
                {'AttributeName': 'Autor', 'AttributeType': 'S'},
                {'AttributeName': 'AttributeName', 'AttributeType': 'S'}, 
                {'AttributeName': 'AttributeValue', 'AttributeType': 'S'},
                {'AttributeName': 'UserID', 'KeyType': 'S'} # OJO: Si usas UserID, debe ser S
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'AutorIndex',
                    'KeySchema': [{'AttributeName': 'Autor', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'GSI_ByAttribute',
                    'KeySchema': [
                        {'AttributeName': 'AttributeName', 'KeyType': 'HASH'},
                        {'AttributeName': 'AttributeValue', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'GSI_User_Ratings',
                    'KeySchema': [{'AttributeName': 'UserID', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        tabla.wait_until_exists()
        print("Tabla creada correctamente.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    crear_tabla()