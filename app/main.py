from app.config.database import init_db
from app.routers import recipe

from fastapi import FastAPI

app = FastAPI()

app.include_router(recipe.router)