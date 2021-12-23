from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
#from starlette.status import HTTP_404_NOT_FOUND
from .. import models, schemas, utils, oath2
from ..database import get_db

router = APIRouter(prefix="/users", tags=['Users'])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    #hash password
    user.password = utils.hash(user.password)
         
    new_user = models.User(**user.dict()) #this unpacks the dictionary and maps them to the fields    
    db.add(new_user) #insert new post
    db.commit() #commit it
    db.refresh(new_user) #pull new post and get info
    return new_user

@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {id} does not exist")

    return user