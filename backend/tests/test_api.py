import asyncio
import httpx
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

TEST_USERS = {
    "manager": {
        "username": "test_manager",
        "email": "manager@test.com",
        "password": "Manager123!",
        "role": "manager" 
    },
    "staff": {
        "username": "test_staff",
        "email": "staff@test.com",
        "password": "Staff123!",
        "role": "staff" 
    }
}

TEST_CATEGORY = {
    "name": "Test Category"
}

TEST_PRODUCT = {
    "name": "Test Product",
    "price": 1999,
    "image_url": "test.jpg"
}

class TestRestaurantAPI:
    def __init__(self):
        self.tokens = {}
        self.created_ids = {}
    
    async def make_request(self, method, url, **kwargs):
        """Make HTTP request with error handling"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                logger.info(f"Making {method} request to {url}")
                if 'json' in kwargs:
                    logger.info(f"Request data: {kwargs['json']}")
                
                response = await client.request(method, f"{BASE_URL}{url}", **kwargs)
                logger.info(f"{method} {url} - Status: {response.status_code}")
                
                if response.status_code >= 400:
                    logger.error(f"Error response: {response.text}")
                else:
                    if response.text:
                        logger.info(f"Response: {response.text[:200]}") 
                
                return response
            except Exception as e:
                logger.error(f"Request failed: {e}")
                import traceback
                traceback.print_exc()
                return None
    
    async def test_server_health(self):
        """Test if server is running"""
        logger.info("\n🔍 Testing server health...")
        response = await self.make_request("GET", "/")
        if response and response.status_code == 200:
            logger.info("Server is running")
            return True
        else:
            logger.error("Server is not responding")
            return False
    
    async def create_test_user(self, user_type: str) -> Dict[str, Any]:
        """Create a test user"""
        logger.info(f"\Creating {user_type} user...")
        user_data = TEST_USERS[user_type]
        
        response = await self.make_request(
            "POST",
            "/users/",
            json=user_data
        )
        
        if response and response.status_code == 201:
            user = response.json()
            self.created_ids[user_type] = user["id"]
            logger.info(f"Created {user_type} user: {user['username']} (ID: {user['id']})")
            return user
        elif response and response.status_code == 400:
            # User might already exist, try to login instead
            logger.info(f"{user_type} user might already exist, trying login...")
            return None
        else:
            logger.error(f"Failed to create {user_type} user")
            return None
    
    async def login_user(self, user_type: str) -> str:
        """Login a user"""
        logger.info(f"\n Logging in as {user_type}...")
        user_data = TEST_USERS[user_type]
        
        response = await self.make_request(
            "POST",
            "/auth/login",
            data={
                "username": user_data["username"],
                "password": user_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response and response.status_code == 200:
            token = response.json()["access_token"]
            self.tokens[user_type] = token
            logger.info(f"Logged in as {user_type}")
            return token
        else:
            logger.error(f"Failed to login as {user_type}")
            return None
    
    async def create_category(self, user_type: str) -> Dict[str, Any]:
        """Create a test category"""
        logger.info(f"\n Creating category as {user_type}...")
        
        if user_type not in self.tokens:
            logger.error(f" No token for {user_type}")
            return None
        
        headers = {"Authorization": f"Bearer {self.tokens[user_type]}"}
        
        response = await self.make_request(
            "POST",
            "/categories/",
            json=TEST_CATEGORY,
            headers=headers
        )
        
        if response and response.status_code == 201:
            category = response.json()
            self.created_ids["category"] = category["id"]
            logger.info(f" Created category: {category['name']} (ID: {category['id']})")
            return category
        else:
            logger.error(f" Failed to create category")
            return None
    
    async def get_categories(self, user_type: str):
        """Get all categories"""
        logger.info(f"\n Getting categories as {user_type}...")
        
        if user_type not in self.tokens:
            logger.error(f"No token for {user_type}")
            return None
        
        headers = {"Authorization": f"Bearer {self.tokens[user_type]}"}
        
        response = await self.make_request(
            "GET",
            "/categories/",
            headers=headers
        )
        
        if response and response.status_code == 200:
            categories = response.json()
            logger.info(f"Got {len(categories)} categories")
            return categories
        else:
            logger.error(f"Failed to get categories")
            return None
    
    async def test_protected_endpoint(self, user_type: str):
        """Test accessing /users/me endpoint"""
        logger.info(f"\n👤 Testing /users/me as {user_type}...")
        
        if user_type not in self.tokens:
            logger.error(f"No token for {user_type}")
            return None
        
        headers = {"Authorization": f"Bearer {self.tokens[user_type]}"}
        
        response = await self.make_request(
            "GET",
            "/auth/me",
            headers=headers
        )
        
        if response and response.status_code == 200:
            user = response.json()
            logger.info(f"Got user info: {user['username']} (Role: {user['role']})")
            return user
        else:
            logger.error(f"Failed to get user info")
            return None
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("="*50)
        logger.info("Starting Restaurant API Tests")
        logger.info("="*50)
        
        # First check if server is running
        if not await self.test_server_health():
            logger.error("Server is not available. Make sure it's running on http://localhost:8000")
            logger.error("Run: uvicorn app.main:app --reload")
            return
        
        # Try to login first (users might already exist)
        logger.info("\n" + "="*50)
        logger.info("Attempting to login...")
        logger.info("="*50)
        
        await self.login_user("manager")
        await self.login_user("staff")
        
        # If login failed, try to create users
        if "manager" not in self.tokens:
            logger.info("\n" + "="*50)
            logger.info("Creating users...")
            logger.info("="*50)
            await self.create_test_user("manager")
            await self.create_test_user("staff")
            
            # Try login again
            await self.login_user("manager")
            await self.login_user("staff")
        
        # Test authenticated endpoints
        if "manager" in self.tokens:
            logger.info("\n" + "="*50)
            logger.info("Testing with Manager token")
            logger.info("="*50)
            
            # Test /users/me
            await self.test_protected_endpoint("manager")
            
            # Test categories
            await self.get_categories("manager")
            await self.create_category("manager")
            await self.get_categories("manager")
        
        if "staff" in self.tokens:
            logger.info("\n" + "="*50)
            logger.info("Testing with Staff token")
            logger.info("="*50)
            
            # Test /users/me
            await self.test_protected_endpoint("staff")
            
            # Test categories
            await self.get_categories("staff")
        
        logger.info("\n" + "="*50)
        logger.info("All tests completed!")
        logger.info("="*50)

async def main():
    tester = TestRestaurantAPI()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())