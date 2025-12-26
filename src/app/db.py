from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import json
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name, region_name="ap-south-1"):
    """Fetch secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in response:
            return json.loads(response['SecretString'])
        else:
            return json.loads(response['SecretBinary'])
    except ClientError as e:
        raise RuntimeError(f"Failed to fetch secret '{secret_name}': {str(e)}")

# Get database credentials from AWS Secrets Manager
secret_name = os.getenv("DB_SECRET_NAME", "app-db-secret")
db_secret = get_secret(secret_name)

DB_HOST = db_secret.get("host") or os.getenv("DATABASE_HOST")
DB_PORT = db_secret.get("port") or os.getenv("DATABASE_PORT", "5432")
DB_NAME = db_secret.get("dbname") or os.getenv("DATABASE_NAME")
DB_USER = db_secret.get("username") or os.getenv("DATABASE_USER")
DB_PASS = db_secret.get("password") or os.getenv("DATABASE_PASSWORD")

if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS]):
    raise RuntimeError("Missing required database credentials in AWS Secrets Manager or environment variables")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
