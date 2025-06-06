import mysql.connector.errorcode
from pydantic import BaseModel, ValidationError, AfterValidator
from typing import List, Dict, Annotated
import requests
from dotenv import dotenv_values
import mysql.connector
from mysql.connector import errorcode

DB_USER, DB_PASS, DB_HOST, DB_NAME = dotenv_values(".env").values()

def is_short(value: str) -> str:
    if len(value) > 448:
        raise ValueError(f"{value} is too long!")
    return value

ShortDesc = Annotated[str, AfterValidator(is_short)]
class Product(BaseModel):
    id: int
    title: str
    price: float
    description: ShortDesc

def extract_products() -> List[Dict]:
    response = []
    try:
        response = requests.get('https://fakestoreapi.com/products')
    except requests.exceptions.RequestException as e:
        print(f"!!! REQUEST FAILED: {e}")
    finally:
        return response.json()
    
def transform_products(raw: List[Dict]) -> List[Product]:
    validated = []
    for item in raw:
        try:
            product = Product(**item)
            validated.append(product)
        except ValidationError as e:
            print(f"Skipping invalid item: {e}")
    return validated

def load_products(products: List[Product]) -> None:
    # connect to database
    conn = mysql.connector.connect(user=DB_USER, password=DB_PASS, database=DB_NAME, host=DB_HOST)
    # create a cursor
    try:
        with conn.cursor() as cursor:
            # set the query
            query = """
                INSERT INTO products (id, title, price, description)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    price = VALUES(price),
                    description = VALUES(description);
                """
            data = [(p.id, p.title, p.price, p.description) for p in products]
            # example: [(69, shrek, 2.5, description), (54, fiona, 1.9, lorem ipsum)]

            # write insert statements to database
            cursor.executemany(query, data)
        conn.commit()
        print(f"Inserted {len(products)} products into the DB")
    except mysql.connector.Error as e:
        print(f"Something went wrong {e}")
    finally:
        conn.close()
