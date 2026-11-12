from pyspark.sql import SparkSession
from src.quality.rules import split_valid_sales, assert_unique

def test_sales_quality_split():
    spark = SparkSession.builder.master("local[1]").appName("quality-test").getOrCreate()
    try:
        df = spark.createDataFrame([
            ("A", "P1", "S1", 2, 10.0, "2026-01-01"),
            ("B", "P1", "S1", 0, 10.0, "2026-01-01"),
        ], ["sale_id", "product_id", "store_id", "quantity", "unit_price", "sale_date"])
        valid, invalid = split_valid_sales(df)
        assert valid.count() == 1
        assert invalid.count() == 1
    finally:
        spark.stop()

def test_unique_key_check():
    spark = SparkSession.builder.master("local[1]").appName("unique-test").getOrCreate()
    try:
        df = spark.createDataFrame([("A",), ("B",)], ["sale_id"])
        assert_unique(df, "sale_id")
    finally:
        spark.stop()
