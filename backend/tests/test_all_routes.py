import asyncio
import httpx
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

TEST_MANAGER = {
    "username": "prem101",
    "email": "prem101@test.com",
    "password": "prempass",
    "role": "manager"
}

TEST_CATEGORY = {"name": "Test Category"}
TEST_CATEGORY_UPDATE = {"name": "Updated Category"}
TEST_PRODUCT = {"name": "Test Product", "price": 1999, "image_url": "test.jpg"}
TEST_PRODUCT_UPDATE = {"name": "Updated Test Product", "price": 2499}
TEST_TABLE = {"table_number": "T67" , "capacity": 4}
TEST_TABLE_STATUS = {"status": "occupied"}
TEST_USER = {"username": "new_staff", "email": "newstaff@test.com", "password": "Staff123!", "role": "staff"}
TEST_CART_ITEM = {"product_id": None, "quantity": 2}
TEST_PAYMENT = {"payment_method": "cash"}

class TestManagerAPI:
    def __init__(self):
        self.token = None
        self.created_ids = {}
        self.passed = []
        self.failed = []
    
    async def make_request(self, method, url, **kwargs):
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(method, f"{BASE_URL}{url}", **kwargs)
                return response
            except Exception as e:
                logger.error(f"Request failed: {e}")
                return None
    
    def log_result(self, name, passed):
        if passed:
            self.passed.append(name)
            logger.info(f"✓ {name}")
        else:
            self.failed.append(name)
            logger.error(f"✗ {name}")
    
    async def test_server_health(self):
        logger.info("\n" + "="*50)
        logger.info("SERVER HEALTH TEST")
        logger.info("="*50)
        response = await self.make_request("GET", "/")
        passed = response and response.status_code == 200
        self.log_result("Server Health", passed)
        return passed
    
    async def login_manager(self):
        logger.info("\n" + "="*50)
        logger.info("MANAGER LOGIN TEST")
        logger.info("="*50)
        response = await self.make_request(
            "POST", "/auth/login",
            data={"username": TEST_MANAGER["username"], "password": TEST_MANAGER["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response and response.status_code == 200:
            self.token = response.json()["access_token"]
            self.log_result("Manager Login", True)
            return True
        self.log_result("Manager Login", False)
        return False
    
    async def test_get_current_user(self):
        logger.info("\n" + "="*50)
        logger.info("GET CURRENT USER TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("GET", "/auth/me", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Current User", passed)
        return passed
    
    async def test_create_category(self):
        logger.info("\n" + "="*50)
        logger.info("CREATE CATEGORY TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("POST", "/categories/", json=TEST_CATEGORY, headers=headers)
        if response and response.status_code == 201:
            self.created_ids["category"] = response.json()["id"]
            self.log_result("Create Category", True)
            return True
        self.log_result("Create Category", False)
        return False
    
    async def test_get_categories(self):
        logger.info("\n" + "="*50)
        logger.info("GET CATEGORIES TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("GET", "/categories/", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Categories", passed)
        return passed
    
    async def test_get_category_by_id(self):
        logger.info("\n" + "="*50)
        logger.info("GET CATEGORY BY ID TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        category_id = self.created_ids.get("category")
        if not category_id:
            self.log_result("Get Category By ID", False)
            return False
        response = await self.make_request("GET", f"/categories/{category_id}", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Category By ID", passed)
        return passed
    
    async def test_update_category(self):
        logger.info("\n" + "="*50)
        logger.info("UPDATE CATEGORY TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        category_id = self.created_ids.get("category")
        if not category_id:
            self.log_result("Update Category", False)
            return False
        response = await self.make_request("PATCH", f"/categories/{category_id}", json=TEST_CATEGORY_UPDATE, headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Update Category", passed)
        return passed
    
    async def test_create_product(self):
        logger.info("\n" + "="*50)
        logger.info("CREATE PRODUCT TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        category_id = self.created_ids.get("category")
        if not category_id:
            self.log_result("Create Product", False)
            return False
        product_data = TEST_PRODUCT.copy()
        product_data["category_id"] = category_id
        response = await self.make_request("POST", "/products/", json=product_data, headers=headers)
        if response and response.status_code == 201:
            self.created_ids["product"] = response.json()["id"]
            self.log_result("Create Product", True)
            return True
        self.log_result("Create Product", False)
        return False
    
    async def test_get_products(self):
        logger.info("\n" + "="*50)
        logger.info("GET PRODUCTS TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("GET", "/products/", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Products", passed)
        return passed
    
    async def test_get_available_products(self):
        logger.info("\n" + "="*50)
        logger.info("GET AVAILABLE PRODUCTS TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("GET", "/products/available", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Available Products", passed)
        return passed
    
    async def test_get_product_by_id(self):
        logger.info("\n" + "="*50)
        logger.info("GET PRODUCT BY ID TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        product_id = self.created_ids.get("product")
        if not product_id:
            self.log_result("Get Product By ID", False)
            return False
        response = await self.make_request("GET", f"/products/{product_id}", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Product By ID", passed)
        return passed
    
    async def test_update_product(self):
        logger.info("\n" + "="*50)
        logger.info("UPDATE PRODUCT TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        product_id = self.created_ids.get("product")
        if not product_id:
            self.log_result("Update Product", False)
            return False
        response = await self.make_request("PATCH", f"/products/{product_id}", json=TEST_PRODUCT_UPDATE, headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Update Product", passed)
        return passed
    
    async def test_create_table(self):
        logger.info("\n" + "="*50)
        logger.info("CREATE TABLE TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("POST", "/tables/", json=TEST_TABLE, headers=headers)
        if response and response.status_code == 201:
            self.created_ids["table"] = response.json()["id"]
            self.log_result("Create Table", True)
            return True
        self.log_result("Create Table", False)
        return False
    
    async def test_get_tables(self):
        logger.info("\n" + "="*50)
        logger.info("GET TABLES TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("GET", "/tables/", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Tables", passed)
        return passed
    
    async def test_get_available_tables(self):
        logger.info("\n" + "="*50)
        logger.info("GET AVAILABLE TABLES TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("GET", "/tables/available", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Available Tables", passed)
        return passed
    
    async def test_get_table_by_id(self):
        logger.info("\n" + "="*50)
        logger.info("GET TABLE BY ID TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        table_id = self.created_ids.get("table")
        if not table_id:
            self.log_result("Get Table By ID", False)
            return False
        response = await self.make_request("GET", f"/tables/{table_id}", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Table By ID", passed)
        return passed
    
    async def test_update_table_status(self):
        logger.info("\n" + "="*50)
        logger.info("UPDATE TABLE STATUS TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        table_id = self.created_ids.get("table")
        if not table_id:
            self.log_result("Update Table Status", False)
            return False
        response = await self.make_request("PATCH", f"/tables/{table_id}/status", json=TEST_TABLE_STATUS, headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Update Table Status", passed)
        return passed
    
    async def test_get_cart(self):
        logger.info("\n" + "="*50)
        logger.info("GET CART TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("GET", "/cart/", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Cart", passed)
        if passed:
            cart_data = response.json()
            self.created_ids["cart"] = cart_data.get("id")
        return passed
    
    async def test_add_to_cart(self):
        logger.info("\n" + "="*50)
        logger.info("ADD TO CART TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        product_id = self.created_ids.get("product")
        if not product_id:
            self.log_result("Add To Cart", False)
            return False
        cart_item = TEST_CART_ITEM.copy()
        cart_item["product_id"] = product_id
        response = await self.make_request("POST", "/cart/add-item", json=cart_item, headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Add To Cart", passed)
        return passed
    
    async def test_update_cart_item(self):
        logger.info("\n" + "="*50)
        logger.info("UPDATE CART ITEM TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("GET", "/cart/", headers=headers)
        if response and response.status_code == 200:
            cart_items = response.json().get("items", [])
            if cart_items:
                item_id = cart_items[0]["id"]
                update_response = await self.make_request("PATCH", f"/cart/update-item/{item_id}?quantity=3", headers=headers)
                passed = update_response and update_response.status_code == 200
                self.log_result("Update Cart Item", passed)
                return passed
        self.log_result("Update Cart Item", False)
        return False
    
    async def test_set_cart_table(self):
        logger.info("\n" + "="*50)
        logger.info("SET CART TABLE TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        table_id = self.created_ids.get("table")
        if not table_id:
            self.log_result("Set Cart Table", False)
            return False
        response = await self.make_request("POST", f"/cart/set-table/{table_id}", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Set Cart Table", passed)
        return passed
    
    async def test_create_order(self):
        logger.info("\n" + "="*50)
        logger.info("CREATE ORDER TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        cart_id = self.created_ids.get("cart")
        if not cart_id:
            self.log_result("Create Order", False)
            return False
        order_data = {
            "cart_id": cart_id,
            "order_type": "takeaway",
            "customer_name": "Test Customer",
            "customer_phone": "1234567890"
        }
        response = await self.make_request("POST", "/orders/checkout", json=order_data, headers=headers)
        if response and response.status_code == 201:
            self.created_ids["order"] = response.json()["id"]
            self.log_result("Create Order", True)
            return True
        self.log_result("Create Order", False)
        return False
    
    async def test_get_orders(self):
        logger.info("\n" + "="*50)
        logger.info("GET ORDERS TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("GET", "/orders/", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Orders", passed)
        return passed
    
    async def test_get_active_orders(self):
        logger.info("\n" + "="*50)
        logger.info("GET ACTIVE ORDERS TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("GET", "/orders/active", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Active Orders", passed)
        return passed
    
    async def test_get_order_by_id(self):
        logger.info("\n" + "="*50)
        logger.info("GET ORDER BY ID TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        order_id = self.created_ids.get("order")
        if not order_id:
            self.log_result("Get Order By ID", False)
            return False
        response = await self.make_request("GET", f"/orders/{order_id}", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Order By ID", passed)
        return passed
    
    async def test_update_order_status(self):
        logger.info("\n" + "="*50)
        logger.info("UPDATE ORDER STATUS TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        order_id = self.created_ids.get("order")
        if not order_id:
            self.log_result("Update Order Status", False)
            return False
        response = await self.make_request("PATCH", f"/orders/{order_id}/status", json={"status": "preparing"}, headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Update Order Status", passed)
        return passed
    
    async def test_process_cash_payment(self):
        logger.info("\n" + "="*50)
        logger.info("PROCESS CASH PAYMENT TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        order_id = self.created_ids.get("order")
        if not order_id:
            self.log_result("Process Cash Payment", False)
            return False
        response = await self.make_request("POST", f"/payments/cash/{order_id}", headers=headers)
        if response and response.status_code == 200:
            self.created_ids["payment"] = response.json().get("payment_id")
            self.log_result("Process Cash Payment", True)
            return True
        self.log_result("Process Cash Payment", False)
        return False
    
    async def test_verify_payment(self):
        logger.info("\n" + "="*50)
        logger.info("VERIFY PAYMENT TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        order_id = self.created_ids.get("order")
        if not order_id:
            self.log_result("Verify Payment", False)
            return False
        response = await self.make_request("GET", f"/payments/verify/{order_id}", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Verify Payment", passed)
        return passed
    
    async def test_get_popular_products(self):
        logger.info("\n" + "="*50)
        logger.info("GET POPULAR PRODUCTS TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("GET", "/recommendations/popular?limit=5", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Get Popular Products", passed)
        return passed
    
    async def test_train_recommendations(self):
        logger.info("\n" + "="*50)
        logger.info("TRAIN RECOMMENDATIONS TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("POST", "/recommendations/train", headers=headers)
        passed = response and response.status_code == 200
        self.log_result("Train Recommendations", passed)
        return passed
    
    async def test_clear_cart(self):
        logger.info("\n" + "="*50)
        logger.info("CLEAR CART TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.make_request("DELETE", "/cart/clear", headers=headers)
        passed = response and response.status_code == 204
        self.log_result("Clear Cart", passed)
        return passed
    
    async def test_delete_table(self):
        logger.info("\n" + "="*50)
        logger.info("DELETE TABLE TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        table_id = self.created_ids.get("table")
        if not table_id:
            self.log_result("Delete Table", False)
            return False
        response = await self.make_request("DELETE", f"/tables/{table_id}", headers=headers)
        passed = response and response.status_code == 204
        self.log_result("Delete Table", passed)
        return passed
    
    async def test_delete_product(self):
        logger.info("\n" + "="*50)
        logger.info("DELETE PRODUCT TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        product_id = self.created_ids.get("product")
        if not product_id:
            self.log_result("Delete Product", False)
            return False
        response = await self.make_request("DELETE", f"/products/{product_id}", headers=headers)
        passed = response and response.status_code == 204
        self.log_result("Delete Product", passed)
        return passed
    
    async def test_delete_category(self):
        logger.info("\n" + "="*50)
        logger.info("DELETE CATEGORY TEST")
        logger.info("="*50)
        headers = {"Authorization": f"Bearer {self.token}"}
        category_id = self.created_ids.get("category")
        if not category_id:
            self.log_result("Delete Category", False)
            return False
        response = await self.make_request("DELETE", f"/categories/{category_id}", headers=headers)
        passed = response and response.status_code == 204
        self.log_result("Delete Category", passed)
        return passed
    
    async def run_all_tests(self):
        logger.info("="*60)
        logger.info("STARTING MANAGER API TESTS")
        logger.info("="*60)
        
        if not await self.test_server_health():
            logger.error("Server not available")
            return
        
        if not await self.login_manager():
            logger.error("Login failed")
            return
        
        await self.test_get_current_user()
        await self.test_create_category()
        await self.test_get_categories()
        await self.test_get_category_by_id()
        await self.test_update_category()
        await self.test_create_product()
        await self.test_get_products()
        await self.test_get_available_products()
        await self.test_get_product_by_id()
        await self.test_update_product()
        await self.test_create_table()
        await self.test_get_tables()
        await self.test_get_available_tables()
        await self.test_get_table_by_id()
        await self.test_update_table_status()
        await self.test_get_cart()
        await self.test_add_to_cart()
        await self.test_update_cart_item()
        await self.test_set_cart_table()
        await self.test_create_order()
        await self.test_get_orders()
        await self.test_get_active_orders()
        await self.test_get_order_by_id()
        await self.test_update_order_status()
        await self.test_process_cash_payment()
        await self.test_verify_payment()
        await self.test_get_popular_products()
        await self.test_train_recommendations()
        await self.test_clear_cart()
        await self.test_delete_table()
        await self.test_delete_product()
        await self.test_delete_category()
        
        logger.info("\n" + "="*60)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("="*60)
        logger.info(f"PASSED: {len(self.passed)} tests")
        logger.info(f"FAILED: {len(self.failed)} tests")
        
        if self.failed:
            logger.info("\nFailed Tests:")
            for test in self.failed:
                logger.info(f"  ✗ {test}")
        
        logger.info("="*60)

async def main():
    tester = TestManagerAPI()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())