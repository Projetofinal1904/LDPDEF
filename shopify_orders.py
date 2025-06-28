import os
import requests
import random
from faker import Faker
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SHOP_NAME = os.getenv("SHOP_NAME")
SHOPIFY_TOKEN = os.getenv("SHOPIFY_TOKEN")
API_VERSION = "2023-10"

if not SHOP_NAME:
    raise ValueError(f"❌ SHOP_NAME inválido: {SHOP_NAME}")

HEADERS = {
    "X-Shopify-Access-Token": SHOPIFY_TOKEN,
    "Content-Type": "application/json"
}

faker = Faker()
Faker.seed(42)
random.seed(42)

ALLOWED_COUNTRIES = {
    "Portugal": None,
    "Espanha": None,
    "França": None,
    "Alemanha": None,
    "Itália": None,
    "Estados Unidos": ["CA", "NY", "TX", "FL", "IL"],
    "Brasil": ["SP", "RJ", "MG", "BA"],
}

def get_products():
    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/products.json?limit=250"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("products", [])
    else:
        print(f"❌ Erro ao buscar produtos: {response.status_code} - {response.text}")
        return []

def generate_customer():
    name = faker.name().split()
    country = random.choice(list(ALLOWED_COUNTRIES.keys()))
    province_list = ALLOWED_COUNTRIES[country]
    province = random.choice(province_list) if province_list else None

    return {
        "first_name": name[0],
        "last_name": name[-1],
        "email": faker.unique.email(),
        "country": country,
        "province": province
    }

def generate_random_date():
    start_date = datetime(2025, 4, 1)
    end_date = datetime.now()
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%dT%H:%M:%S")

def create_order(products):
    customer = generate_customer()
    num_items = random.randint(1, 5)
    selected_products = random.sample(products, min(num_items, len(products)))

    line_items = []
    for product in selected_products:
        variant = product["variants"][0]
        line_items.append({
            "variant_id": variant["id"],
            "quantity": random.randint(1, 3)
        })

    shipping_address = {
        "first_name": customer["first_name"],
        "last_name": customer["last_name"],
        "address1": faker.street_address(),
        "city": faker.city(),
        "country": customer["country"],
        "zip": faker.postcode()
    }

    if customer["province"]:
        shipping_address["province_code"] = customer["province"]

    order_data = {
        "order": {
            "email": customer["email"],
            "financial_status": "paid",
            "created_at": generate_random_date(),
            "line_items": line_items,
            "shipping_address": shipping_address
        }
    }

    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/orders.json"
    response = requests.post(url, headers=HEADERS, json=order_data)

    if response.status_code == 201:
        order = response.json().get("order", {})
        print(f"✅ Encomenda criada: {order.get('id')} | {customer['country']} | {customer['province']}")
    else:
        print(f"❌ Erro ({response.status_code}): {response.text}")

# Executar
products = get_products()
if products:
    for _ in range(20):
        create_order(products)
else:
    print("⚠️ Nenhum produto encontrado.")
