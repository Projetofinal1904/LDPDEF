# Gera encomendas simuladas com produtos reais no Shopify
import os
import requests
import random
from faker import Faker
from datetime import datetime, timedelta

# === CONFIG ===
SHOP_NAME = os.getenv("SHOP_NAME", "yyfrbw-fj.myshopify.com")
SHOPIFY_TOKEN = os.getenv("SHOPIFY_TOKEN")
API_VERSION = "2023-10"

HEADERS = {
    "X-Shopify-Access-Token": SHOPIFY_TOKEN,
    "Content-Type": "application/json"
}

faker = Faker()
Faker.seed(42)
random.seed(42)

# Lista de países permitidos (Europa, EUA e Brasil)
ALLOWED_COUNTRIES = [
    "Portugal", "Espanha", "França", "Alemanha", "Itália", "Países Baixos", "Bélgica", "Suécia", "Noruega",
    "Suíça", "Áustria", "Irlanda", "Dinamarca", "Polónia", "Grécia", "Finlândia", "Hungria", "Roménia",
    "Estados Unidos", "Brasil"
]

# === Obter produtos reais ===
def get_products():
    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/products.json?limit=250"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("products", [])
    else:
        print(f"❌ Erro ao buscar produtos: {response.status_code}")
        return []

# === Gerar cliente fictício ===
def generate_customer():
    name = faker.name().split()
    country = random.choice(ALLOWED_COUNTRIES)
    return {
        "first_name": name[0],
        "last_name": name[-1],
        "email": faker.email(),
        "country": country
    }

# === Criar data aleatória entre abril 2025 e hoje ===
def generate_random_date():
    start_date = datetime(2025, 4, 1)
    end_date = datetime(2025, 6, 23)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%dT%H:%M:%S%z")

# === Criar encomenda no Shopify ===
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

    order_date = generate_random_date()

    order_data = {
        "order": {
            "email": customer["email"],
            "financial_status": "paid",
            "created_at": order_date,
            "line_items": line_items,
            "shipping_address": {
                "first_name": customer["first_name"],
                "last_name": customer["last_name"],
                "address1": faker.street_address(),
                "city": faker.city(),
                "province": faker.state(),
                "country": customer["country"],
                "zip": faker.postcode()
            }
        }
    }

    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/orders.json"
    response = requests.post(url, headers=HEADERS, json=order_data)

    if response.status_code == 201:
        order = response.json().get("order", {})
        print(f"✅ Encomenda ID {order.get('id')} criada para {customer['email']} em {customer['country']} na data {order_date}")
    else:
        print(f"❌ Erro ao criar encomenda: {response.status_code} - {response.text}")

# === Executar ===
products = get_products()
if products:
    for _ in range(20):  # cria 20 encomendas por execução
        create_order(products)
else:
    print("⚠️ Nenhum produto encontrado.")
