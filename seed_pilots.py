import psycopg2
from datetime import datetime
import random

# Database connection parameters
DB_NAME = "drone_db"
DB_USER = "drone_user"
DB_PASSWORD = "drone_password"
DB_HOST = "localhost"
DB_PORT = "5432"

def generate_pilot_data(num_pilots=10):
    first_names = ["Азамат", "Айбек", "Алмас", "Асхат", "Бауржан", "Дамир", "Ерлан", "Жандар", "Кайрат", "Марат", 
                  "Нурлан", "Рахат", "Серик", "Талгат", "Шынгыс", "Айгуль", "Айнур", "Алтынай", "Гульнара", "Динара",
                  "Жанна", "Зухра", "Кунсулу", "Майра", "Назгуль", "Самал", "Салтанат", "Шолпан"]
    last_names = ["Абдуллаев", "Ахметов", "Баймуханов", "Бектаев", "Досмагамбетов", "Ермеков", "Жакиев", "Ибраев",
                 "Каримов", "Куанышев", "Мамаев", "Нурмагамбетов", "Омаров", "Рахимов", "Садыков", "Темирбаев",
                 "Уалиев", "Хасанов", "Шарипов", "Ыскаков"]
    
    pilots = []
    for i in range(num_pilots):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        phone = f"+7700{random.randint(1000000, 9999999)}"
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        
        pilots.append({
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': phone,
            'email': email
        })
    
    return pilots

def seed_pilots():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Generate pilot data
        pilots = generate_pilot_data()
        
        # Prepare the insert query
        insert_query = """
        INSERT INTO pilots (first_name, last_name, phone_number, email)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (email) DO NOTHING;
        """
        
        # Insert the data
        for pilot in pilots:
            cur.execute(insert_query, (
                pilot['first_name'],
                pilot['last_name'],
                pilot['phone_number'],
                pilot['email']
            ))
        
        # Commit the changes
        conn.commit()
        
        print(f"Successfully seeded {len(pilots)} pilot records!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    seed_pilots() 