from uuid import UUID
from datetime import timedelta
from decouple import config as env

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from itsdangerous import URLSafeTimedSerializer
from pydantic import EmailStr

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, PasswordReset
from app.utils.mail import send_verification_email, send_password_reset_email
from app.utils.auth import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

serializer = URLSafeTimedSerializer(env('SECRET_KEY'))

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, background_tasks: BackgroundTasks, session: Session = Depends(get_db)) -> UserResponse:
    existing_user = session.query(User).filter(
        or_(User.email == body.email, User.username == body.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User with this username or email already exists'
        )

    hashed_pwd = hash_password(body.password)

    new_user = User(
        name=body.name,
        email=body.email,
        username=body.username,
        password=hashed_pwd
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    token = serializer.dumps(new_user.email, salt='email-verification')

    background_tasks.add_task(
        send_verification_email,
        new_user.email,
        new_user.username,
        token
    )    

    return new_user

@router.get('/verify-email', status_code=status.HTTP_200_OK)
async def verify_email(token:str, session: Session = Depends(get_db)):
    try:
        # max_age = 3600 means the link is valid for an hour
        email = serializer.loads(token, salt='email-verification', max_age=3600)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid or expired token'
        )
    
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    user.is_verified = True
    session.commit()

    return {'message':'Email verified successfully'}

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

@router.post('/password-reset-request', status_code=status.HTTP_200_OK)
async def password_reset_request(body: PasswordReset, background_tasks: BackgroundTasks, session: Session = Depends(get_db)):
    user = session.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    token = serializer.dumps(user.email, salt='password-reset')

    background_tasks.add_task(
        send_password_reset_email,
        user.email,
        user.username,
        token      
    )

    return {'message': 'Password reset email sent successfully'}

@router.put('/reset-password', status_code=status.HTTP_200_OK)
async def reset_password(token: str, new_password:str, session: Session = Depends(get_db)):
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid or expired token'
        )

    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    hashed_password = hash_password(new_password)
    user.password = hashed_password
    session.commit()

    return {"message": "Password reset successfully."}

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_user(id: UUID, session: Session = Depends(get_db)) -> UserResponse:
    user = session.query(User).get(id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with the ID {id} not found'
        )

    return user