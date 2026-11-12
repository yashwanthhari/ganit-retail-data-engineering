from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
SOURCE_DIR = DATA_DIR / "source"
LAKE_DIR = DATA_DIR / "lake"
BRONZE_DIR = LAKE_DIR / "bronze"
SILVER_DIR = LAKE_DIR / "silver"
GOLD_DIR = LAKE_DIR / "gold"
QUARANTINE_DIR = DATA_DIR / "quarantine"

DATASETS = ("customers", "products", "stores", "sales", "inventory")
