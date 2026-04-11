
# OrderDeck - Restaurant POS System - Full Stack FastAPI + React

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Uvicorn](https://img.shields.io/badge/Uvicorn-6B6B6B?style=for-the-badge&logo=uvicorn&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLModel](https://img.shields.io/badge/SQLModel-FF6C37?style=for-the-badge)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-FF0000?style=for-the-badge)
![Alembic](https://img.shields.io/badge/Alembic-8B4513?style=for-the-badge)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-CA4245?style=for-the-badge&logo=react-router&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Zustand](https://img.shields.io/badge/Zustand-000000?style=for-the-badge)
![Axios](https://img.shields.io/badge/Axios-5A29E4?style=for-the-badge&logo=axios&logoColor=white)
![Recharts](https://img.shields.io/badge/Recharts-22B5BF?style=for-the-badge)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

**A complete Restaurant Point of Sale system with order management, table tracking, dynamic cart, recommendation system,
payment processing, and analytics dashboard. Built with FastAPI, React, and PostgreSQL.**

## Features

### Order Management
- **Dine-in & Takeaway** - Support for both dining and takeout orders
- **Real-time Order Status** - Track orders from pending to completed
- **Order History** - Complete order history with filters

### Table Management
- **Table Occupancy Tracking** - Real-time table status (available/occupied)
- **Customer Assignment** - Assign customers to tables with name tracking
- **Table Reset** - Bulk reset functionality for end of day
- **Capacity Management** - Track table capacities

### Payment Processing
- **Multiple Payment Methods** - Cash and eSewa integration
- **Digital Receipts** - Download and print receipts
- **Payment Verification** - Track payment status

### Analytics Dashboard
- **Revenue Tracking** - Daily, weekly revenue charts
- **Order Analytics** - Track order volume and patterns
- **Payment Method Breakdown** - Visualize payment distribution
- **Popular Products** - Identify best-selling items

### Smart Cart System
- **Real-time Updates** - Instant cart updates
- **Product Recommendations** - Collaborative filtering based cross-selling suggestions
- **Quantity Management** - Easy item quantity controls
- **Order Type Selection** - Seamless dine-in/takeaway toggle

### Authentication & Authorization
- **JWT Authentication** - Secure token-based auth
- **Role-Based Access** - Manager, Staff roles
- **Protected Routes** - Granular permission system

### Responsive Design
- **Mobile-First** - Works on all screen sizes
- **Touch Optimized** - Perfect for tablets and touchscreens

## Architecture

### Backend (FastAPI)
- **RESTful API** - Well-documented endpoints
- **Async Support** - High-performance async operations
- **SQLModel ORM** - Type-safe database operations
- **PostgreSQL** - Reliable data persistence

### Frontend (React)
- **State Management** - Zustand for global state
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization

### Infrastructure
- **Docker Compose** - Container orchestration
- **Nginx** - Static file serving and reverse proxy
- **PostgreSQL** - Production-ready database

### File Structure
```bash
orderdeck/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── utils.py
│   │   ├── auth.py
│   │   ├── permissions.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── categories.py
│   │   │   ├── products.py
│   │   │   ├── tables.py
│   │   │   ├── cart.py
│   │   │   ├── orders.py
│   │   │   ├── payments.py
│   │   │   └── recommendations.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── recommendation.py
│   ├──  assets/
│   │ └── products/
│   │    └── [product images...]
│   ├── migrations/
│   │   ├── versions/
│   │   │   ├── 001_initial_migration.py
│   │   │   ├── 002_add_party_id.py
│   │   │   └── 003_add_transaction_id.py
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_all_routes.py
│   │   └── test_api.py
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── .env
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   ├── Layout.jsx
│   │   │   │   ├── Header.jsx
│   │   │   │   └── Sidebar.jsx
│   │   │   ├── Menu/
│   │   │   │   ├── MenuList.jsx
│   │   │   │   ├── MenuCard.jsx
│   │   │   │   └── CategoryTabs.jsx
│   │   │   ├── Cart/
│   │   │   │   ├── CartSidebar.jsx
│   │   │   │   └── CartItem.jsx
│   │   │   ├── Orders/
│   │   │   │   └── OrderCard.jsx
│   │   │   ├── Tables/
│   │   │   │   └── TableCard.jsx
│   │   │   ├── Payment/
│   │   │   │   ├── PaymentModal.jsx
│   │   │   │   └── Receipt.jsx
│   │   │   ├── Settings/
│   │   │   │   ├── UsersTab.jsx
│   │   │   │   ├── CategoriesTab.jsx
│   │   │   │   ├── ProductsTab.jsx
│   │   │   │   ├── RecommendationsTab.jsx
│   │   │   │   ├── UserModal.jsx
│   │   │   │   ├── CategoryModal.jsx
│   │   │   │   ├── ProductModal.jsx
│   │   │   │   └── SeedDataModal.jsx
│   │   │   └── Notification/
│   │   │       └── NotificationSidebar.jsx
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Menu.jsx
│   │   │   ├── Orders.jsx
│   │   │   ├── OrderDetails.jsx
│   │   │   ├── Tables.jsx
│   │   │   ├── Payments.jsx
│   │   │   ├── Analytics.jsx
│   │   │   ├── Settings.jsx
│   │   │   ├── PaymentSuccess.jsx
│   │   │   └── PaymentFailure.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── auth.service.js
│   │   │   ├── category.service.js
│   │   │   ├── product.service.js
│   │   │   ├── table.service.js
│   │   │   ├── cart.service.js
│   │   │   ├── order.service.js
│   │   │   ├── payment.service.js
│   │   │   └── recommendation.service.js
│   │   ├── store/
│   │   │   ├── cartStore.js
│   │   │   └── orderStore.js
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── utils/
│   │   │   ├── notificationHelper.js
│   │   │   └── paymentUtils.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── nginx.conf
│   ├── .env
│   ├── Dockerfile
│   └── .gitignore
├── docker-compose.yml
├── docker-compose-img.yml
├── .gitignore
├── README.md
└── LICENSE.md
```
## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 22+ 
- Python 3.14+ 

## Configuration

1. **Clone the repository**
```bash
   git clone https://github.com/Priyansh-A/orderdeck.git
    cd orderdeck
```
2. **Create a .env file in the backend directory and add**
   ```bash
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=postgres
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   SECRET_KEY=(your unique key in sha256 hash)
   ```

3. **Build the images**
  ```bash
    docker-compose build
```    
4. **Run the container**
 ```bash
   docker-compose up
   ```
5. **Application urls**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000
   - api endpoints (Swagger UI) : http://localhost:8000/docs

6. **Sign in to the website**
   - Frontend: http://localhost:5173/login
7. **Seed menu data in the website**
   
   ![alt text](</screenshots/Screenshot 2026-04-10 223114.png>)

8. **After some successful orders train the recommendation system to give product recommendations based on purchase history**

   ![alt text](</screenshots/Screenshot 2026-04-10 232911.png>)
   
### All routes in the backend (localhost:8000) 
   ![alt text](</screenshots/Screenshot 2026-04-10 212654.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 212713.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 212726.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 212740.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 212759.png>)

### Frontend functionality screenshots
   ![alt text](</screenshots/Screenshot 2026-04-10 174357.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174425.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174447.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174527.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174551.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174603.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174641.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 232854.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174654.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174708.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174654.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174716.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174730.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174759.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174815.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 174826.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 175004.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 175021.png>)
   ![alt text](</screenshots/Screenshot 2026-04-10 175053.png>)

   ---
## 📄 License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

Copyright © 2026 Prem Raj Awasthi & Prabhav Sthapit

<div align="center">
  <sub>Built with ❤️ | OrderDeck POS System</sub>
</div>



