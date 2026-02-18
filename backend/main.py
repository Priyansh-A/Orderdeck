from fastapi import FastAPI
from .database import engine, create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import category, product
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
import os
from pathlib import Path

@asynccontextmanager 
async def lifespan(app: FastAPI): 
    # startup
    create_db_and_tables()
    yield
    # shutdown
    print("Database connections closed")

app = FastAPI(lifespan=lifespan) 


app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


assets_path = Path(__file__).parent / "assets"
app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

app.include_router(category.router)
app.include_router(product.router)
# app.include_router(auth.router)
# app.include_router(like.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}

