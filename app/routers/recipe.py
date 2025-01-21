from app.config.database import get_db
from app.helpers.enums import MealType
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

router = APIRouter(
    prefix="/recipes",
    tags=["recipe"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_recipe(body: RecipeCreate, session: Session = Depends(get_db)) -> RecipeResponse:
    recipe = Recipe(
        name=body.name,
        description=body.description,
        ingredients=body.ingredients,
        instructions=body.instructions,
        servings=body.servings,
        meal_type=body.meal_type
    )

    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return recipe

@router.get("/", status_code=status.HTTP_200_OK)
async def get_recipes(session: Session = Depends(get_db)) -> List[RecipeResponse]:
    recipes = session.query(Recipe).all()
    return recipes

@router.get("/filter", status_code=status.HTTP_200_OK)
async def filter_recipe_by_meal_type(type: MealType, session: Session = Depends(get_db)) -> List[RecipeResponse]:
    recipes = session.query(Recipe).filter_by(meal_type=type).all()

    if not recipes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No recipes found with meal type {type.value}'
        )

    return recipes

@router.get("/search", status_code=status.HTTP_200_OK)
async def search_recipe(name:str, session: Session = Depends(get_db)):
    recipes = session.query(Recipe).filter(Recipe.name.ilike(f'%{name}%')).all()

    if not recipes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No recipes found with name containing, {name}'
        )

    return recipes

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_recipe_with_id(id: UUID, session: Session = Depends(get_db)) -> RecipeResponse:
    recipe = session.query(Recipe).get(id)

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Recipe with ID, {id} does not exist'
        )
        
    return recipe

@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_recipe(id: UUID, body: RecipeUpdate, session: Session = Depends(get_db)) -> RecipeResponse:
    recipe = session.query(Recipe).get(id)

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Recipe with ID, {id} not found'
        )

    for key, value in body.dict(exclude_unset=True).items():
        setattr(recipe, key, value)

    session.commit()
    session.refresh(recipe)
    
    return recipe

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(id: UUID, session: Session = Depends(get_db)) -> None:
    recipe = session.query(Recipe).get(id)

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Recipe with ID, {id} not found.'
        )

    session.delete(recipe)
    session.commit()
