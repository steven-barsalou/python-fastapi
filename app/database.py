#for using the sql alchemy ORM (object relational mapper)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

#the raw postgres connectors
# import psycopg2 #used for connecting to postgres database
# from psycopg2.extras import RealDictCursor #used to get the column names of the fields as the base package does not include them

#the following string is built from environment variables that are being set in the .env file
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# dependency, we will call this each time we need to connect to the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#create database connection if you need to run raw sql
# while True:
#     try:
#         #normally we wouldn't code these variables in here, we would have
#         conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='Fuck!1234', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print('database connection was successful!')
#         break
#     except Exception as error:
#         print('connecting to database failed')
#         print('error:', error)
#     time.sleep(2)
#     print('retrying connection')
