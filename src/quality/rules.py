from pyspark.sql import functions as F

def split_valid_sales(df):
    """Separate valid sales from rows that fail basic business rules."""
    invalid = (
        F.col("sale_id").isNull()
        | F.col("product_id").isNull()
        | F.col("store_id").isNull()
        | F.col("quantity").isNull()
        | (F.col("quantity") <= 0)
        | F.col("unit_price").isNull()
        | (F.col("unit_price") < 0)
        | F.col("sale_date").isNull()
    )
    return df.filter(~invalid), df.filter(invalid)

def assert_unique(df, key):
    duplicates = df.groupBy(key).count().filter(F.col("count") > 1).limit(1).count()
    if duplicates:
        raise ValueError(f"Duplicate business key detected: {key}")
