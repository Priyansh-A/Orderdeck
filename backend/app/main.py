from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .database import engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import category, product, user, user_auth, tables, orders, cart, recommendations, payments
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from .scripts.seed_manager import seed_initial_manager
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
    await seed_initial_manager()
    print("Manager seeding completed")
    yield
    # shutdown
    await engine.dispose()
    print("Database connections closed")


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        if "/docs" in request.url.path or "/openapi.json" in request.url.path:
            return response
        
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' http://localhost:5173 https://rc-epay.esewa.com.np https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https: http:; "
            "font-src 'self' data:; "
            "connect-src 'self' http://localhost:8000 http://localhost:5173 https://rc-epay.esewa.com.np;"
        )
        return response

app = FastAPI(lifespan=lifespan)

# CSP middleware
app.add_middleware(CSPMiddleware)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1"]
)

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
    return {"message": "Hello World"}

