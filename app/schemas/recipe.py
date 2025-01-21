from app.helpers.enums import MealType
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class RecipeBase(BaseModel):
    name : str
    description: str
    ingredients: str
    instructions: str
    servings: str
    meal_type: MealType

class RecipeCreate(RecipeBase):
    pass

class RecipeUpdate(BaseModel):
    name : Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[str] = None
    instructions: Optional[str] = None
    servings: Optional[str] = None
    meal_type: Optional[MealType] = None


class RecipeResponse(RecipeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



