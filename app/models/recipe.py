from app.models.base import BaseModel
from ..helpers.enums import MealType
from sqlalchemy import Column, String, Enum

class Recipe(BaseModel):
    __tablename__ = 'recipe'

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    ingredients = Column(String, nullable=False)
    instructions = Column(String, nullable=False)
    servings = Column(String, nullable=False)
    meal_type = Column(Enum(MealType), nullable=False)

