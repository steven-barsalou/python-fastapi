from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #requires passlib library with bcrypt: pip install passlib['bcrypt']

def hash(password: str):
    return pwd_context.hash(password)

#return true if inbound password matches stored password
def verify(plain_password: str, hased_password: str):
    return pwd_context.verify(plain_password, hased_password)