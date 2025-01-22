from uuid import UUID
from datetime import timedelta
from decouple import config as env

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.utils.auth import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, session: Session = Depends(get_db)) -> UserResponse:
    hashed_pwd = hash_password(body.password)

    user = User(
        name=body.name,
        email=body.email,
        username=body.username,
        password=hashed_pwd
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(body: UserLogin, session: Session = Depends(get_db)):
    user = session.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invalid credentials!'
        )
    
    if not verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invalid credentials'
        )

    access_token_expires = timedelta(minutes=int(env('ACCESS_TOKEN_EXPIRE_MINUTES')))
    access_token = create_access_token(
        data={'sub':user.username},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type='bearer')


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_user(id: UUID, session: Session = Depends(get_db)):
    user = session.query(User).get(id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with the ID {id} not found'
        )

    return user