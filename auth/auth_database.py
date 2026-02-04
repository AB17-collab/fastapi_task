from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import quote

MYSQL_USER = "root"
MYSQL_PASSWORD = "Debarnab34@"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DATABASE = "fastapi_db"

# URL-encode the password to handle special characters
ENCODED_PASSWORD = quote(MYSQL_PASSWORD, safe='')
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{ENCODED_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

##Connection
engine = create_engine(DATABASE_URL)

##Session Local
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

## Base

Base = declarative_base()
