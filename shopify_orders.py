import os
import requests
import random
from faker import Faker
from datetime import datetime, timedelta

SHOP_NAME = os.getenv("SHOP_NAME")
SHOPIFY_TOKEN = os.getenv("SHOPIFY_TOKEN")
API_VERSION = "2023-10"

HEADERS = {
    "X-Shopify-Access-Token": SHOPIFY_TOKEN,
    "Content-Type": "application/json"
}

faker = Faker()
Faker.seed(42)
random.seed(42)

# Dicionário de países: código ISO → nome completo
COUNTRIES = {
    "PT": "Portugal",
    "ES": "Espanha",
    "FR": "França",
    "DE": "Alemanha",
    "IT": "Itália",
    "NL": "Países Baixos",
    "BE": "Bélgica",
    "SE": "Suécia",
    "NO": "Noruega",
    "CH": "Suíça",
    "AT": "Áustria",
    "IE": "Irlanda",
    "DK": "Dinamarca",
    "PL": "Polónia",
    "GR": "Grécia",
    "FI": "Finlândia",
    "HU": "Hungria",
    "RO": "Roménia",
    "US": "Estados Unidos",
    "BR": "Brasil"
}

def get_products():
    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/products.json?limit=250"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("products", [])
    else:
        print(f"Erro ao buscar produtos: {response.status_code}")
        return []

def generate_customer():
    name = faker.name().split()
    country_code = random.choice(list(COUNTRIES.keys()))
    return {
        "first_name": name[0],
        "last_name": name[-1],
        "email": faker.email(),
        "country_code": country_code,
        "country_name": COUNTRIES[country_code]
    }

def generate_random_date():
    start_date = datetime(2025, 4, 1)
    end_date = datetime.now()
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).isoformat()

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

    order_data = {
        "order": {
            "email": customer["email"],
            "financial_status": "paid",
            "created_at": generate_random_date(),
            "note": f"País: {customer['country_name']}",
            "line_items": line_items,
            "shipping_address": {
                "first_name": customer["first_name"],
                "last_name": customer["last_name"],
                "address1": faker.street_address(),
                "city": faker.city(),
                "province": "Lisboa",  # fixo para evitar erros
                "country_code": customer["country_code"],
                "zip": faker.postcode()
            }
        }
    }

    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/orders.json"
    response = requests.post(url, headers=HEADERS, json=order_data)

    if response.status_code == 201:
        order = response.json().get("order", {})
        print(f"✅ Encomenda ID {order.get('id')} criada para {customer['email']} ({customer['country_name']})")
    else:
        print(f"❌ Erro ao criar encomenda: {response.status_code} - {response.text}")

# Executar
products = get_products()
if produ
