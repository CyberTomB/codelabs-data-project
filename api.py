from pydantic import BaseModel, ValidationError
from typing import List, Dict
import requests

# id, title, price, description

class Product(BaseModel):
    id: int
    title: str
    price: float
    description: str

def fetch_products() -> List[Dict]:
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
