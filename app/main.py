from app.config.database import init_db
from app.routers import recipe, user

from fastapi import FastAPI

app = FastAPI()

app.include_router(recipe.router)
app.include_router(user.router)