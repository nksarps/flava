from app.helpers.enums import MealType
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class RecipeBase(BaseModel):
    name : str
    description: str
    ingredients: str
    instructions: str
    servings: str
    meal_type: MealType

class RecipeCreate(RecipeBase):
    pass

class RecipeResponse(RecipeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



