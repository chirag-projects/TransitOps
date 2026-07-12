import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import url as url_module

from dotenv import load_dotenv

load_dotenv()

username = os.environ["DB_USERNAME"]
password = os.environ["DB_PASSWORD"]
host = os.environ["DB_HOST"]
port = os.environ["DB_PORT"]
db = os.environ["DB_NAME"]

DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{db}"


def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    # Connect to default postgres database to create our database
    admin_url = f"postgresql://{username}:{password}@{host}:{port}/postgres"
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    
    with admin_engine.connect() as conn:
        # Check if database exists
        result = conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{db}'")
        )
        if result.fetchone() is None:
            conn.execute(text(f"CREATE DATABASE {db}"))
            print(f"✓ Database '{db}' created successfully")
        else:
            print(f"✓ Database '{db}' already exists")
    
    admin_engine.dispose()


# Create database if it doesn't exist
create_database_if_not_exists()

engine = create_engine(url=DATABASE_URL, 
                       pool_size=20, 
                       pool_pre_ping=True, 
                       pool_recycle=3600)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
