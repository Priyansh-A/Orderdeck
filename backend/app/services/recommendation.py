import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
from sqlmodel import select
from typing import List, Dict, Any, Set
from collections import defaultdict
import json
from datetime import datetime, timedelta

from ..database import SessionDep
from ..models import Order, OrderItem, Product, CartItem


class RecommendationService:
    """Apriori-based recommendation system for product suggestions"""
    
    def __init__(self, session: SessionDep):
        self.session = session
        self.frequent_itemsets = None
        self.rules = None
        self.product_map = {}
        self.last_trained = None
    
    async def load_order_data(self, days_back: int = 30) -> pd.DataFrame:
        """Load historical order data for training"""
        
        # Calculate date threshold
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        query = (
            select(Order)
            .where(
                Order.created_at >= cutoff_date,
                Order.status == "completed",
                Order.payment_status == "paid"
            )
        )
        result = await self.session.exec(query)
        orders = result.all()
        
        transaction_data = []
        
        for order in orders:
            # Get items for this order
            items_query = select(OrderItem).where(OrderItem.order_id == order.id)
            items_result = await self.session.exec(items_query)
            items = items_result.all()
            
            products = [item.product_id for item in items]
            transaction_data.append(products)
        
        return transaction_data
    
    async def train_model(self, min_support: float = 0.01, min_confidence: float = 0.5):
        """Train the Apriori model with transaction data"""
        
        # Load transaction data
        transactions = await self.load_order_data(days_back=30)
        
        if not transactions:
            print("No transaction data available for training")
            return False
        
        # Create a mapping of product IDs to names
        products = await self.session.exec(select(Product))
        self.product_map = {p.id: p.name for p in products.all()}
        
        # Get all unique product IDs
        all_products = list(set([item for sublist in transactions for item in sublist]))
        
        # Create DataFrame
        data = []
        for transaction in transactions:
            row = {product: (product in transaction) for product in all_products}
            data.append(row)
        
        df = pd.DataFrame(data)
        
        df = df.fillna(False)
        
        # Algorithm
        self.frequent_itemsets = apriori(
            df, 
            min_support=min_support, 
            use_colnames=True,
            verbose=1
        )
        
        # Generate association rules
        if len(self.frequent_itemsets) > 0:
            self.rules = association_rules(
                self.frequent_itemsets,
                metric="confidence",
                min_threshold=min_confidence
            )
            
            # Sort rules by lift for better recommendations
            self.rules = self.rules.sort_values('lift', ascending=False)
            
            self.last_trained = datetime.now()
            return True
        
        return False
    
    async def get_recommendations_for_cart(
        self, 
        cart_items: List[CartItem],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get product recommendations based on current cart items
        """
        if not cart_items:
            return await self.get_popular_products(limit)
        
        if self.rules is None or self.rules.empty:
            await self.train_model()
        
        if self.rules is None or self.rules.empty:
            return await self.get_popular_products(limit)
        
        # Get product IDs in cart
        cart_product_ids = set([item.product_id for item in cart_items])
        
        # Find recommendations from association rules
        recommendations = defaultdict(float)
        
        for rule in self.rules.itertuples():
            antecedents = set(rule.antecedents)
            consequents = set(rule.consequents)
            
            if antecedents.issubset(cart_product_ids):
                for product_id in consequents:
                    if product_id not in cart_product_ids:
                        recommendations[product_id] += rule.lift
        
        recommended_products = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
        
        result = []
        for product_id, score in recommended_products:
            product = await self.session.get(Product, product_id)
            if product and product.is_available:
                result.append({
                    "product_id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "image_url": product.image_url,
                    "recommendation_score": round(score, 2),
                    "reason": "Frequently bought together"
                })
        
        # If not enough recommendations, fill with popular products
        if len(result) < limit:
            popular = await self.get_popular_products(limit - len(result))
            for item in popular:
                if item["product_id"] not in [r["product_id"] for r in result]:
                    result.append(item)
        
        return result
    
    async def get_popular_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most popular products from order history"""
        
        query = (
            select(OrderItem.product_id, OrderItem.quantity)
            .join(Order)
            .where(
                Order.status == "completed",
                Order.payment_status == "paid"
            )
        )
        result = await self.session.exec(query)
        items = result.all()
        
        product_counts = defaultdict(int)
        for product_id, quantity in items:
            product_counts[product_id] += quantity
        
        top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        recommendations = []
        for product_id, count in top_products:
            product = await self.session.get(Product, product_id)
            if product and product.is_available:
                recommendations.append({
                    "product_id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "image_url": product.image_url,
                    "recommendation_score": round(min(count / 10, 5), 2),
                    "reason": "Popular choice"
                })
        
        return recommendations
    
    async def get_related_products(
        self, 
        product_id: int, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get products frequently bought with a specific product"""
        
        if self.rules is None or self.rules.empty:
            await self.train_model()
        
        if self.rules is None or self.rules.empty:
            return await self.get_popular_products(limit)
        
        recommendations = defaultdict(float)
        
        for rule in self.rules.itertuples():
            antecedents = set(rule.antecedents)
            consequents = set(rule.consequents)
            
            if product_id in antecedents:
                for rec_id in consequents:
                    if rec_id != product_id:
                        recommendations[rec_id] += rule.lift
            
            if product_id in consequents:
                for rec_id in antecedents:
                    if rec_id != product_id:
                        recommendations[rec_id] += rule.lift
        
        recommended_products = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
        
        result = []
        for rec_id, score in recommended_products:
            product = await self.session.get(Product, rec_id)
            if product and product.is_available:
                result.append({
                    "product_id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "image_url": product.image_url,
                    "recommendation_score": round(score, 2),
                    "reason": "Customers also bought"
                })
        
        if len(result) < limit:
            popular = await self.get_popular_products(limit - len(result))
            for item in popular:
                if item["product_id"] not in [r["product_id"] for r in result]:
                    result.append(item)
        
        return result