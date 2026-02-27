from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .database import engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import category, product, user, user_auth
from contextlib import asynccontextmanager
import os
from pathlib import Path
from . import models
import logging
import traceback


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start connectiom
    async with engine.begin() as conn:
        await conn.run_sync(models.SQLModel.metadata.create_all)
    print("Database tables created")
    yield
    # shutdown
    await engine.dispose()
    print("Database connections closed")


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],      
)


assets_path = Path(__file__).parent / "assets"
app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

app.include_router(category.router)
app.include_router(product.router)
app.include_router(user.router)
app.include_router(user_auth.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}

