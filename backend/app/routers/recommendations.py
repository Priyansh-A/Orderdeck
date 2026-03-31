from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlmodel import select

from ..database import SessionDep
from .. import schemas, auth
from ..models import Cart, CartItem
from ..permissions import Permission
from ..services.recommendation import RecommendationService

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/cart/{cart_id}", response_model=List[schemas.ProductRecommendationOut])
async def get_cart_recommendations(
    session: SessionDep,
    cart_id: int,
    limit: int = 5,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_MENU]))
):
    """Get product recommendations based on current cart items"""
    query = (
        select(Cart)
        .where(Cart.id == cart_id)
        .options(selectinload(Cart.items))
    )
    result = await session.exec(query)
    cart = result.first()
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    rec_service = RecommendationService(session)
    
    recommendations = await rec_service.get_recommendations_for_cart(
        cart.items,
        limit=limit
    )
    
    return recommendations


@router.get("/product/{product_id}", response_model=List[schemas.ProductRecommendationOut])
async def get_product_recommendations(
    session: SessionDep,
    product_id: int,
    limit: int = 5,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_MENU]))
):
    """Get products frequently bought with the specified product"""
    rec_service = RecommendationService(session)
    recommendations = await rec_service.get_related_products(product_id, limit=limit)
    
    return recommendations


@router.post("/train", status_code=200)
async def train_recommendation_model(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.MANAGE_MENU])),
    min_support: float = 0.01,
    min_confidence: float = 0.5
):
    """Manually trigger model training (admin only)"""
    rec_service = RecommendationService(session)
    success = await rec_service.train_model(min_support, min_confidence)
    
    if success:
        return {
            "message": "Recommendation model trained successfully",
            "rules_count": len(rec_service.rules) if rec_service.rules is not None else 0
        }
    else:
        return {
            "message": "Training failed - insufficient data",
            "rules_count": 0
        }


@router.get("/popular", response_model=List[schemas.ProductRecommendationOut])
async def get_popular_products(
    session: SessionDep,
    limit: int = 5,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_MENU]))
):
    """Get most popular products"""
    rec_service = RecommendationService(session)
    recommendations = await rec_service.get_popular_products(limit)
    
    return recommendations