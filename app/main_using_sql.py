#run "uvicorn app.main:app --reload" at terminal to run program and webserver for testing with postman
#main is the file, app is the FastAPI application
# --reload restarts the server reach time the code is saved

# the url http://127.0.0.1:8000/docs will give you the swagger API documentation
# the url http://127.0.0.1:8000/redoc will give you the redoc API documentation

from typing import Optional
from fastapi import FastAPI, Response, status, Depends
from fastapi.exceptions import HTTPException
from fastapi.params import Body
from pydantic import BaseModel
import time #used for sleep()

import psycopg2 #used for connecting to postgres database
from psycopg2.extras import RealDictCursor #used to get the column names of the fields as the base package does not include them

from .database import engine, get_db
from sqlalchemy.orm import Session

from . import models
from .config import settings

#this is the command that actually creates the tables in postgres that were defined by models.py
#if the table already exists, it will remain, otherwise it will be created
models.Base.metadata.create_all(bind=engine)

#create classs Post from the BaseModel and give it the attributes title, content, published, and rating
class Post(BaseModel):
    title: str
    content: str
    published: bool


#create database connection
while True:
    try:
        #normally we wouldn't code these variables in here, we would have
        conn = psycopg2.connect(host=settings.database_hostname, database=settings.database_name, user=settings.database_username, password=settings.database_password, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('database connection was successful!')
        break
    except Exception as error:
        print('connecting to database failed')
        print('error:', error)
    time.sleep(2)
    print('retrying connection')


#initialize my_posts dictionary content with two records/tuples
my_posts = [{"id": 1, "title": "title of post 1", "content": "content of post 1"},
    {"id": 2, "title": "title of post 2", "content": "content of post 2"}]

#create an instance of FastAPI called app
app = FastAPI()

#--------------------------FastAPI decorators--------------------------#
#FastAPI will look down the set of decorators and find the first match, so order could matter


#root call, returns hellow worlds
@app.get("/")
def root():
    return {"message": "Hello World!"}

#posts, will return all of the posts in json
@app.get("/posts")
def get_posts():
    cursor.execute("""Select * From posts;""")
    posts = cursor.fetchall() 
    
    return {"data": posts}

#post by id, get a single post by id, if not found throw a 404 status, else return the post details
@app.get("/posts/{id}")
def get_post(id: int, response: Response): #function has access to id from path parameter and FastAPI is going to do validation to make sure that the parameter is of the correct type, otherwise will throw an error

    cursor.execute("""Select * From posts Where id = %s;""", (str(id),)) #not sure why but the last , needs to be there to make this code work correctly

    post = cursor.fetchone()
    if not post:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")

    return {"post_detail": post}

#create a new post and return 201 status
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post):

    #using the %s parameters helps sanitize the input and prevent things like sql injection
    cursor.execute("""Insert Into posts (title, content, published) Values (%s, %s, %s) Returning *""", (new_post.title, new_post.content, new_post.published))
    new_post_record = cursor.fetchone() #get the record returned by the insert returning command
    conn.commit() #force the record to be saved
    print(new_post_record)
    return {"data": "created post"}


#delete a post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT) #update the status code to a 204, in FastAPI a 204 does not allow data to be returned, such as a message
def delete_post(id: int):
    
    cursor.execute("""Delete From posts Where id = %s Returning *""", (str(id),)) #not sure why but the last , needs to be there to make this code work correctly
    post = cursor.fetchone()
    conn.commit() #force the record to be saved

    #if not found, return a 404 status
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with  id: {id} does not exist")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


#update an existing post by id
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
   
    #using the %s parameters helps sanitize the input and prevent things like sql injection
    cursor.execute("""Update posts Set title = %s, content = %s, published=%s Where id = %s Returning *""", (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone() #get the record returned by the insert returning command
    conn.commit() #force the record to be saved
    
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with  id: {id} does not exist")
    
    print(post)

    return {"data": updated_post}

@app.get("/sqlalchemy")
def test_post(db: Session = Depends(get_db)):
    
    return {"status": "success"}