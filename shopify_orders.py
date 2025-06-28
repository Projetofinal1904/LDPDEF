import os
import pandas as pd
import requests
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

SHOP_NAME = os.getenv("SHOP_NAME")
ACCESS_TOKEN = os.getenv("SHOPIFY_TOKEN")
NEON_URL = os.getenv("NEON_URL")

HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

API_VERSION = "2023-10"

def fetch_data(endpoint, params=None):
    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/{endpoint}.json"
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro {response.status_code} ao aceder a {endpoint}")
        return {}

def sync_table(df, table_name, id_column):
    engine = create_engine(NEON_URL)
    with engine.connect() as conn:
        existing = pd.read_sql(f"SELECT {id_column} FROM {table_name}", conn) if engine.dialect.has_table(conn, table_name) else pd.DataFrame(columns=[id_column])
        novos = df[~df[id_column].isin(existing[id_column])]
        if not novos.empty:
            try:
                novos.to_sql(table_name, conn, if_exists='append', index=False)
                print(f"✅ {len(novos)} novos registos adicionados a {table_name}")
            except Exception as e:
                print(f"❌ Erro ao escrever em {table_name}:", e)

def process_orders():
    orders = fetch_data('orders', {'limit': 250, 'status': 'any'})
    raw_orders = orders.get('orders', [])

    data = []
    for order in raw_orders:
        country = order.get('shipping_address', {}).get('country')
        if country:  # Só guarda se o país existir
            data.append({
                'order_id': order['id'],
                'created_at': order['created_at'],
                'country': country
            })

    df = pd.DataFrame(data)
    if not df.empty:
        sync_table(df, 'orders', 'order_id')
    else:
        print("Nenhuma encomenda com país disponível encontrada.")

if __name__ == "__main__":
    process_orders()

