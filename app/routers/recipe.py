from app.config.database import get_db
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/recipes",
    tags=["recipe"]
)

@router.post("/")
async def create_recipe(body: RecipeCreate, db: Session = Depends(get_db)):
    recipe = Recipe(
        name=body.name,
        description=body.description,
        ingredients=body.ingredients,
        instructions=body.ingredients,
        servings=body.servings,
        meal_type=body.meal_type  
    )

    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return recipe

@router.get("/", response_model=List[RecipeResponse])
def get_recipes(db: Session = Depends(get_db)):
    recipes = db.query(Recipe).all()
    return recipes

