"""Local PySpark medallion pipeline. Re-running a date replaces that date's output."""
import argparse
from datetime import date
from pathlib import Path
from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
from src.common.config import SOURCE_DIR, BRONZE_DIR, SILVER_DIR, GOLD_DIR, QUARANTINE_DIR
from src.quality.rules import split_valid_sales, assert_unique

def spark_session():
    return (SparkSession.builder.appName("RetailMedallionETL")
            .master("local[*]")
            .config("spark.sql.shuffle.partitions", "4")
            .getOrCreate())

def read_csv(spark, path):
    return spark.read.option("header", True).option("inferSchema", True).csv(str(path))

def write_partition(df, base: Path, run_date: str):
    target = base / f"run_date={run_date}"
    if target.exists():
        import shutil
        shutil.rmtree(target)
    df.write.mode("overwrite").parquet(str(target))

def run(run_date: str):
    drop = SOURCE_DIR / f"drop_date={run_date}"
    if not drop.exists():
        raise FileNotFoundError(f"No source drop found: {drop}")
    spark = spark_session()
    try:
        inputs = {name: read_csv(spark, drop / f"{name}.csv")
                  for name in ("customers", "products", "stores", "sales", "inventory")}
        for name, df in inputs.items():
            write_partition(df.withColumn("_ingested_at", F.current_timestamp())
                            .withColumn("_source_file", F.lit(f"{name}.csv")),
                            BRONZE_DIR / name, run_date)

        # Silver reference data: retain latest CDC image for each business key.
        customers = inputs["customers"].dropDuplicates(["customer_id"])
        products = inputs["products"].dropDuplicates(["product_id"])
        stores = inputs["stores"].dropDuplicates(["store_id"])
        inventory = inputs["inventory"].dropDuplicates(["snapshot_date", "store_id", "product_id"])

        sales = (inputs["sales"]
                 .withColumn("sale_date", F.to_date("sale_date"))
                 .withColumn("quantity", F.col("quantity").cast("integer"))
                 .withColumn("unit_price", F.col("unit_price").cast("double"))
                 .withColumn("discount_amount", F.col("discount_amount").cast("double"))
                 .dropDuplicates(["sale_id"]))
        valid_sales, bad_sales = split_valid_sales(sales)
        write_partition(bad_sales, QUARANTINE_DIR / "sales", run_date)

        # Referential integrity checks; unmatched facts are quarantined.
        valid_sales = (valid_sales.join(products.select("product_id"), "product_id", "inner")
                      .join(stores.select("store_id"), "store_id", "inner")
                      .join(customers.select("customer_id"), "customer_id", "inner"))
        enriched = (valid_sales.join(products, "product_id", "left")
                    .join(stores, "store_id", "left")
                    .join(customers.select("customer_id", "segment"), "customer_id", "left")
                    .withColumn("gross_sales", F.col("quantity") * F.col("unit_price"))
                    .withColumn("net_sales", F.col("gross_sales") - F.col("discount_amount")))
        assert_unique(enriched, "sale_id")

        write_partition(customers, SILVER_DIR / "customers", run_date)
        write_partition(products, SILVER_DIR / "products", run_date)
        write_partition(stores, SILVER_DIR / "stores", run_date)
        write_partition(inventory, SILVER_DIR / "inventory", run_date)
        write_partition(enriched, SILVER_DIR / "sales", run_date)

        gold_sales = enriched.select(
            "sale_id", "sale_date", "customer_id", "segment", "product_id",
            "product_name", "category", "store_id", "store_name", "region",
            "quantity", "unit_price", "discount_amount", "gross_sales", "net_sales"
        )
        daily = (gold_sales.groupBy("sale_date", "store_id", "store_name", "region")
                 .agg(F.countDistinct("sale_id").alias("transaction_count"),
                      F.sum("quantity").alias("units_sold"),
                      F.round(F.sum("gross_sales"), 2).alias("gross_sales"),
                      F.round(F.sum("net_sales"), 2).alias("net_sales")))
        stock_alerts = (inventory.join(products.select("product_id", "product_name", "category"), "product_id")
                        .join(stores.select("store_id", "store_name", "region"), "store_id")
                        .filter(F.col("on_hand_qty") <= F.col("reorder_level")))
        write_partition(gold_sales, GOLD_DIR / "fact_sales", run_date)
        write_partition(daily, GOLD_DIR / "daily_store_sales", run_date)
        write_partition(stock_alerts, GOLD_DIR / "stock_reorder_alerts", run_date)
        print(f"Pipeline completed for {run_date}: {gold_sales.count()} valid sales")
    finally:
        spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    run(parser.parse_args().date)
