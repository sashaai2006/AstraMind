from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pyjwt import encode
from schemas import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, 'secret_key', algorithm='HS256')
    return encoded_jwt

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail='Could not validate credentials', headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_user(db: Session, username: str):
    return db.query(User).filter(User.email == username).first()
