#run "uvicorn app.main:app --reload" at terminal to run program and webserver for testing with postman
#main is the file, app is the FastAPI application

# the url http://127.0.0.1:8000/docs will give you the swagger API documentation
# the url http://127.0.0.1:8000/redoc will give you the redoc API documentation

from fastapi import FastAPI
from .database import engine
from . import models
from .routers import posts, users, authenticate, vote #this gets the functions and decorators from the /routers/posts.py and users.py files

from fastapi.middleware.cors import CORSMiddleware

#this is the command that actually creates the tables in postgres that were defined by models.py
#if the table already exists, it will remain, otherwise it will be created
#no longer needed now that alembic will create the tables upon calling it
#models.Base.metadata.create_all(bind=engine)

#create an instance of FastAPI called app
app = FastAPI()

#this list of strings allows us to configure what domains can make a request of this api, you could also make it ["*""]
origins = ["http://localhost", "https://www.google.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#point to the router for the various files with decorators and functions
app.include_router(posts.router) #this includes the decorators/routes from posts file
app.include_router(users.router) #this includes the decorators/routes from users file
app.include_router(authenticate.router) #this includes the decorators/routes from users file
app.include_router(vote.router) #this includes the decorators/routes from users file

#root call, returns hellow worlds
@app.get("/")
def root():
    return {"message": "Hello World!"}