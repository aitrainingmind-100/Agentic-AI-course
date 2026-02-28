from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
products_db: Dict[str, 'Product'] = {
    "1": {"id": "1", "name": "Product A", "description": "Description of Product A", "price": 29.99, "stock": 100, "category": "Electronics"},
    "2": {"id": "2", "name": "Product B", "description": "Description of Product B", "price": 49.99, "stock": 50, "category": "Home"},
    "3": {"id": "3", "name": "Product C", "description": "Description of Product C", "price": 19.99, "stock": 200, "category": "Books"},
    "4": {"id": "4", "name": "Product D", "description": "Description of Product D", "price": 99.99, "stock": 30, "category": "Clothing"},
    "5": {"id": "5", "name": "Product E", "description": "Description of Product E", "price": 15.99, "stock": 150, "category": "Toys"},
}

orders_db: Dict[str, 'Order'] = {}

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    stock: int
    category: str

class OrderItem(BaseModel):
    productId: str
    quantity: int

class Order(BaseModel):
    id: str
    customerId: str
    products: List[OrderItem]
    totalAmount: float
    status: str
    createdAt: str

@app.get("/products", response_model=List[Product])
def get_products():
    return list(products_db.values())

@app.get("/products/{id}", response_model=Product)
def get_product(id: str):
    product = products_db.get(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/orders", response_model=Order)
def create_order(order: Order):
    total_amount = sum(products_db[item.productId].price * item.quantity for item in order.products)
    order_id = f"order_{len(orders_db) + 1}"
    order_data = Order(
        id=order_id,
        customerId=order.customerId,
        products=order.products,
        totalAmount=total_amount,
        status="pending",
        createdAt=datetime.utcnow().isoformat()
    )
    orders_db[order_id] = order_data
    return order_data

@app.get("/orders/{id}", response_model=Order)
def get_order(id: str):
    order = orders_db.get(id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order