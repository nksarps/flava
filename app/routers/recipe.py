import redis, json
from app.config.database import get_db
from app.helpers.enums import MealType
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate
from app.utils.auth import get_current_user
from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]
)

rd = redis.Redis(host='localhost', port=6379, db=0)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_recipe(
    body: RecipeCreate, 
    session: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> RecipeResponse:
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
async def get_recipes(
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> List[RecipeResponse]:

    cached = rd.get('recipes')

    if cached:
        print('cache hit!')
        return json.loads(cached)
    
    recipes = session.query(Recipe).all()

    recipes_response = [
        {
            "id": str(recipe.id), 
            "name": recipe.name,
            "description": recipe.description,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "servings": recipe.servings,
            "meal_type": recipe.meal_type,
            "created_at": recipe.created_at.isoformat(),
            "updated_at": recipe.updated_at.isoformat(),  
        }
        for recipe in recipes
    ]


    print('cache miss!')
    rd.setex('recipes', 1800, json.dumps(recipes_response))

    return recipes_response

@router.get("/filter", status_code=status.HTTP_200_OK)
async def filter_recipe_by_meal_type(
    type: MealType, 
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[RecipeResponse]:
    cache_key = f'recipes:meal_type:{type.value}'

    cached = rd.get(cache_key)
    if cached:
        print('cache hit!')
        return json.loads(cached)

    recipes = session.query(Recipe).filter_by(meal_type=type).all()

    if not recipes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No recipes found with meal type {type.value}'
        )

    recipes_response = [
        {
            "id": str(recipe.id),
            "name": recipe.name,
            "description": recipe.description,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "servings": recipe.servings,
            "meal_type": recipe.meal_type,
            "created_at": recipe.created_at.isoformat(),
            "updated_at": recipe.updated_at.isoformat()
        } for recipe in recipes
    ]

    print('cache miss!')
    rd.setex(cache_key, 3600, json.dumps(recipes_response))

    return recipes_response

@router.get("/search", status_code=status.HTTP_200_OK)
async def search_recipe(
    name:str, 
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[RecipeResponse]:
    cache_key = f"recipes:search:{name.lower()}"
    cached = rd.get(cache_key)

    if cached:
        print("cache hit!")
        return json.loads(cached)

    recipes = session.query(Recipe).filter(Recipe.name.ilike(f'%{name}%')).all()

    if not recipes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No recipes found with name containing, {name}'
        )

    recipes_response = [
        {
            "id": str(recipe.id),
            "name": recipe.name,
            "description": recipe.description,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "servings": recipe.servings,
            "meal_type": recipe.meal_type,
            "created_at": recipe.created_at.isoformat(),
            "updated_at": recipe.updated_at.isoformat()
        } for recipe in recipes
    ]

    print("cache miss!")
    rd.setex(cache_key, 1800, json.dumps(recipes_response))

    return recipes_response

@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_recipe_with_id(
    id: UUID, 
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RecipeResponse:
    cache_key = f"recipe:{id}"
    cached = rd.get(cache_key)

    if cached:
        print("cache hit!")
        return json.loads(cached)

    recipe = session.query(Recipe).get(id)

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Recipe with ID, {id} does not exist'
        )

    recipe_response = {
        "id": str(recipe.id),
        "name": recipe.name,
        "description": recipe.description,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "servings": recipe.servings,
        "meal_type": recipe.meal_type,
        "created_at": recipe.created_at.isoformat(),
        "updated_at": recipe.updated_at.isoformat(),
    }
        
    print("cache miss!")
    rd.setex(cache_key, 1800, json.dumps(recipe_response))

    return recipe_response

@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_recipe(
    id: UUID, 
    body: RecipeUpdate, 
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RecipeResponse:
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
async def delete_recipe(
    id: UUID, 
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    cache_key = f"recipe:{id}"

    recipe = session.query(Recipe).get(id)

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Recipe with ID, {id} not found.'
        )

    session.delete(recipe)
    session.commit()

    rd.delete(cache_key)

    print(f"Cache for recipe {id} has been invalidated.")

    return None
