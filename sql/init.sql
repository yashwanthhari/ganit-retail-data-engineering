CREATE SCHEMA IF NOT EXISTS retail_mart;

CREATE TABLE IF NOT EXISTS retail_mart.dim_product (
  product_id VARCHAR(20) PRIMARY KEY,
  product_name TEXT NOT NULL,
  category TEXT,
  unit_cost NUMERIC(12,2),
  unit_price NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS retail_mart.dim_store (
  store_id VARCHAR(20) PRIMARY KEY,
  store_name TEXT NOT NULL,
  city TEXT,
  region TEXT
);

CREATE TABLE IF NOT EXISTS retail_mart.fact_sales (
  sale_id VARCHAR(40) PRIMARY KEY,
  sale_date DATE NOT NULL,
  customer_id VARCHAR(20),
  product_id VARCHAR(20) REFERENCES retail_mart.dim_product(product_id),
  store_id VARCHAR(20) REFERENCES retail_mart.dim_store(store_id),
  quantity INTEGER NOT NULL,
  gross_sales NUMERIC(14,2),
  discount_amount NUMERIC(14,2),
  net_sales NUMERIC(14,2)
);

CREATE INDEX IF NOT EXISTS ix_fact_sales_date ON retail_mart.fact_sales(sale_date);
CREATE INDEX IF NOT EXISTS ix_fact_sales_store ON retail_mart.fact_sales(store_id);
