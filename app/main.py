from app.config.database import init_db
from app.routers import recipe

from fastapi import FastAPI

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(recipe.router)