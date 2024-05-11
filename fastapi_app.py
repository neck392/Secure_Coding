from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI()

class Purchase(BaseModel):
    buyer_id: int
    product_id: int
    purchase_time: str
    payment_status: str
    buyer_address: str

class User(BaseModel):
    username: str
    full_name: str
    address: str
    payment_info: str

def create_connection():
    conn = sqlite3.connect('shopping_mall.db')
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            full_name TEXT,
            address TEXT,
            payment_info TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            category TEXT,
            price REAL,
            thumbnail_url TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY,
            buyer_id INTEGER,
            product_id INTEGER,
            purchase_time TEXT,
            payment_status TEXT,
            buyer_address TEXT,
            FOREIGN KEY(buyer_id) REFERENCES users(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    conn.commit()

def add_user(conn, username, password, role, full_name, address, payment_info):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, role, full_name, address, payment_info) VALUES (?, ?, ?, ?, ?, ?)',
                   (username, password, role, full_name, address, payment_info))
    conn.commit()
    user = {"username": username, "password": password, "role": role, "full_name": full_name, "address": address, "payment_info": payment_info}
    return {"message": "User created successfully!", "user": user}

def register_admin(conn, username, password, full_name):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)',
                   (username, password, 'admin', full_name))
    conn.commit()
    user = {"username": username, "password": password, "role": 'admin', "full_name": full_name}
    return {"message": "Admin registered successfully!", "user": user}

def authenticate_user(conn, username, password):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    if user:
        user_info = {"username": user[1], "password": user[2], "role": user[3], "full_name": user[4], "address": user[5], "payment_info": user[6]}
        return {"message": f"Welcome back, {username}!", "user": user_info}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

def get_all_products(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    return [{"id": product[0], "name": product[1], "category": product[2], "price": product[3], "thumbnail_url": product[4]} for product in products]

def add_product(conn, name, category, price, thumbnail_url):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (name, category, price, thumbnail_url) VALUES (?, ?, ?, ?)', (name, category, price, thumbnail_url))
    conn.commit()
    return {"message": "Product added successfully!"}

def delete_product(conn, product_name):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE name = ?', (product_name,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Product '{product_name}' not found")
    conn.commit()
    return {"message": f"Product '{product_name}' deleted successfully!"}

def update_user_info(conn, username, full_name, address, payment_info):
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET full_name = ?, address = ?, payment_info = ? WHERE username = ?', (full_name, address, payment_info, username))
    conn.commit()
    return {"message": "User information updated successfully!"}

def get_user_by_username(conn, username):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    return cursor.fetchone()

def get_all_users(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    return [{"username": user[0], "full_name": user[1], "address": user[2], "payment_info": user[3]} for user in users]

def add_purchase(conn, buyer_id, product_id, payment_status, buyer_address):
    cursor = conn.cursor()
    purchase_time = datetime.now().isoformat()
    cursor.execute('INSERT INTO purchases (buyer_id, product_id, purchase_time, payment_status, buyer_address) VALUES (?, ?, ?, ?, ?)',
                   (buyer_id, product_id, purchase_time, payment_status, buyer_address))
    conn.commit()
    return {"message": "Purchase added successfully!"}

def get_all_purchases(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM purchases')
    purchases = cursor.fetchall()
    return [{"buyer_id": purchase[1], "product_id": purchase[2], "purchase_time": purchase[3], "payment_status": purchase[4], "buyer_address": purchase[5]} for purchase in purchases]

@app.on_event("startup")
async def startup_event():
    conn = create_connection()
    create_tables(conn)
    if not get_user_by_username(conn, "admin"):
        register_admin(conn, "admin", "admin", "Admin User")
    conn.close()

@app.post("/register")
async def register_user(username: str, password: str, role: str, full_name: str, address: Optional[str] = None, payment_info: Optional[str] = None):
    conn = create_connection()
    result = add_user(conn, username, password, role, full_name, address, payment_info)
    conn.close()
    return result

@app.get("/login")
async def login(username: str, password: str):
    conn = create_connection()
    result = authenticate_user(conn, username, password)
    conn.close()
    return result

@app.get("/products", response_model=List[dict])
async def get_products():
    conn = create_connection()
    products = get_all_products(conn)
    conn.close()
    return products

@app.post("/add_product")
async def add_new_product(name: str, category: str, price: float, thumbnail_url: str):
    conn = create_connection()
    result = add_product(conn, name, category, price, thumbnail_url)
    conn.close()
    return result

@app.delete("/products/{product_name}")
async def delete_product_endpoint(product_name: str):
    conn = create_connection()
    result = delete_product(conn, product_name)
    conn.close()
    return result

@app.post("/update_user_info")
async def update_user_info_endpoint(username: str, full_name: str, address: str, payment_info: str):
    conn = create_connection()
    result = update_user_info(conn, username, full_name, address, payment_info)
    conn.close()
    return result

@app.post("/add_purchase")
async def add_purchase_endpoint(purchase: Purchase):
    conn = create_connection()
    result = add_purchase(conn, purchase.buyer_id, purchase.product_id, purchase.payment_status, purchase.buyer_address)
    conn.close()
    return result

@app.get("/purchases", response_model=List[Purchase])
async def get_purchases():
    conn = create_connection()
    purchases = get_all_purchases(conn)
    conn.close()
    return purchases

@app.get("/users", response_model=List[User])
async def get_users():
    conn = create_connection()
    users = get_all_users(conn)
    conn.close()
    return users
