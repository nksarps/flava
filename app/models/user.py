from app.models.base import BaseModel

from sqlalchemy import Column, String

class User(BaseModel):
    __tablename__ = 'users'

    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    