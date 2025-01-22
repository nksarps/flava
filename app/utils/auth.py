import jwt
from jwt.exceptions import InvalidTokenError

from datetime import timedelta, datetime, timezone
from decouple import config as env

from typing import Annotated
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.config.database import get_db
from app.models.user import User
from app.schemas.user import TokenData

from sqlalchemy.orm import Session


pwd_content = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str):
    return pwd_content.hash(password)


def verify_password(plain_pwd: str, hashed_pwd:str):
    return pwd_content.verify(plain_pwd, hashed_pwd)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode =  data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({'exp':expire})
    encoded_jwt = jwt.encode(to_encode, env('JWT_SECRET'), algorithm=env('JWT_ALGORITHM'))
    return encoded_jwt

# THE CODE BELOW VERIFIES THE JWT AND RETURNS THE USER
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        payload = jwt.decode(token, env('JWT_SECRET'), algorithms=[env('JWT_ALGORITHM')])

        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception  

    user = session.query(User).filter(User.username == username).first()

    if user is None:
        raise credentials_exception
    return user



