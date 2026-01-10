from database.mongodb_handler import MongoDBHandler
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

def create_sample_data():
    db = MongoDBHandler()
    
    # Create sample users
    users = []
    for i in range(20):
        user = {
            "id": f"USER{i:03d}",
            "name": fake.name(),
            "email": fake.email(),
            "age": random.randint(18, 65),
            "address": fake.address(),
            "created_at": fake.date_time_this_year()
        }
        users.append(user)
    
    # Create sample products
    products = []
    categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
    for i in range(30):
        product = {
            "id": f"PROD{i:03d}",
            "name": fake.catch_phrase(),
            "category": random.choice(categories),
            "price": round(random.uniform(10, 1000), 2),
            "stock": random.randint(0, 100),
            "description": fake.text(max_nb_chars=100),
            "created_at": fake.date_time_this_year()
        }
        products.append(product)
    
    # Create sample orders
    orders = []
    for i in range(15):
        user = random.choice(users)
        num_products = random.randint(1, 5)
        order_products = []
        total = 0
        
        for _ in range(num_products):
            product = random.choice(products)
            quantity = random.randint(1, 3)
            order_products.append({
                "product_id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity
            })
            total += product["price"] * quantity
        
        order = {
            "id": f"ORD{i:03d}",
            "user_id": user["id"],
            "products": order_products,
            "total_amount": round(total, 2),
            "status": random.choice(["pending", "shipped", "delivered", "cancelled"]),
            "created_at": fake.date_time_this_year()
        }
        orders.append(order)
    
    # Insert into database
    for user in users:
        db.insert_user(user)
    
    for product in products:
        db.insert_product(product)
    
    for order in orders:
        db.insert_order(order)
    
    print("Sample data created successfully!")
    print(f"Users: {len(users)}")
    print(f"Products: {len(products)}")
    print(f"Orders: {len(orders)}")

if __name__ == "__main__":
    create_sample_data()