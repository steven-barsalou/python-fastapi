from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, utils, oath2
from ..database import get_db

#this prefixes all of the decorators in this file with /post
#prefix =  a prefix to the url path in the decorator
#tags = a logical grouping in the swagger documentation at <api_url>/docs
router = APIRouter(tags=['Login'])

#posts, will return all of the posts in json
@router.post("/login", response_model=schemas.Token) #, response_model=List[schemas.LoginResponse]) #List creates a list of class PostResponse
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    #OAuth2PasswordRequestForm has two attributes
    #when using OAuth2PasswordRequestForm the inbound data is expected in the Body form-data
    #username
    #password
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid credentials")

    #create a token
    access_token = oath2.create_access_token(data={"user_id": user.id})

    #return token
    return {"access_token": access_token, "token_type": "bearer"}