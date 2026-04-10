from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .database import engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import category, product, user, user_auth, tables, orders, cart, recommendations, payments
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# media
assets_path = Path(__file__).parent / "assets"
app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

# routes
app.include_router(category.router)
app.include_router(product.router)
app.include_router(user.router)
app.include_router(user_auth.router)
app.include_router(tables.router)
app.include_router(orders.router)
app.include_router(cart.router)
app.include_router(payments.router)
app.include_router(recommendations.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

