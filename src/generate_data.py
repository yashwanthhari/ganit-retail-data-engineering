"""Create deterministic synthetic retail source drops for local ETL practice."""
import argparse
from datetime import date, timedelta
from pathlib import Path
import random
import pandas as pd
from src.common.config import SOURCE_DIR

def generate(run_date: str, seed: int = 42):
    random.seed(seed + int(run_date.replace("-", "")))
    day = date.fromisoformat(run_date)
    out = SOURCE_DIR / f"drop_date={run_date}"
    out.mkdir(parents=True, exist_ok=True)

    customers = pd.DataFrame([
        {"customer_id": f"C{i:05d}", "customer_name": f"Customer {i}",
         "city": random.choice(["Chennai", "Bengaluru", "Hyderabad", "Pune"]),
         "segment": random.choice(["Consumer", "Corporate", "Small Business"]),
         "updated_at": f"{day.isoformat()}T08:00:00"}
        for i in range(1, 501)
    ])
    products = pd.DataFrame([
        {"product_id": f"P{i:04d}", "product_name": f"Product {i}",
         "category": random.choice(["Grocery", "Electronics", "Home", "Fashion"]),
         "unit_cost": round(random.uniform(20, 800), 2),
         "unit_price": round(random.uniform(50, 1200), 2),
         "updated_at": f"{day.isoformat()}T07:00:00"}
        for i in range(1, 101)
    ])
    if day.day > 1:
        # Simulate CDC updates to a small subset of existing products/customers.
        products.loc[0, "unit_price"] = round(float(products.loc[0, "unit_price"]) * 1.04, 2)
        products.loc[0, "updated_at"] = f"{day.isoformat()}T09:30:00"
        customers.loc[0, "segment"] = "Corporate"
        customers.loc[0, "updated_at"] = f"{day.isoformat()}T09:45:00"

    stores = pd.DataFrame([
        {"store_id": f"S{i:03d}", "store_name": f"Store {i}",
         "city": city, "region": region}
        for i, (city, region) in enumerate([
            ("Chennai", "South"), ("Bengaluru", "South"),
            ("Hyderabad", "South"), ("Pune", "West"),
            ("Mumbai", "West"), ("Delhi", "North")
        ], start=1)
    ])
    sales_rows = []
    for i in range(1, 1001):
        product = f"P{random.randint(1, 100):04d}"
        store = f"S{random.randint(1, 6):03d}"
        qty = random.randint(1, 5)
        price = float(products.loc[int(product[1:]) - 1, "unit_price"])
        sale_day = day - timedelta(days=1) if i == 1 and day.day > 1 else day
        sales_rows.append({
            "sale_id": f"{run_date.replace('-', '')}-{i:06d}",
            "customer_id": f"C{random.randint(1, 500):05d}",
            "product_id": product, "store_id": store,
            "sale_date": sale_day.isoformat(), "quantity": qty,
            "unit_price": price, "discount_amount": round(random.uniform(0, 30), 2),
            "updated_at": f"{day.isoformat()}T12:{i % 60:02d}:00"
        })
    inventory = pd.DataFrame([
        {"snapshot_date": day.isoformat(), "store_id": f"S{s:03d}",
         "product_id": f"P{p:04d}", "on_hand_qty": random.randint(0, 80),
         "reorder_level": 15}
        for s in range(1, 7) for p in range(1, 101)
    ])
    for name, frame in {
        "customers": customers, "products": products, "stores": stores,
        "sales": pd.DataFrame(sales_rows), "inventory": inventory
    }.items():
        frame.to_csv(out / f"{name}.csv", index=False)
    print(f"Generated {len(sales_rows)} sales and reference data in {out}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    generate(args.date, args.seed)
