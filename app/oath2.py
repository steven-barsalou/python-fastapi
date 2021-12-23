#required to have pip install python-jose[cryptography]
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings

#this defines where the oath2 is created: /login
oath2_scheme = OAuth2PasswordBearer(tokenUrl='login')

def create_access_token(data: dict):
    to_encode = data.copy()
    expiration_time = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expiration_time})

    return jwt.encode(to_encode, settings.secret_key, settings.algorithm)


def verify_access_token(token: str, credentials_exception):

    try:
        decoded_token = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        id: str = decoded_token.get("user_id")

        if id is None:
            raise credentials_exception
        
        #get the id from the input schema
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    #just returns user id
    return token_data

def get_current_user(token: str = Depends(oath2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id==token.id).first()
    
    return user