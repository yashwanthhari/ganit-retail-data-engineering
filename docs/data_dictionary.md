# Data dictionary

| Dataset | Grain | Business key | Important columns |
|---|---|---|---|
| customers | one customer image | customer_id | customer_name, city, segment, updated_at |
| products | one product image | product_id | product_name, category, unit_cost, unit_price, updated_at |
| stores | one store | store_id | store_name, city, region |
| sales | one transaction line | sale_id | customer_id, product_id, store_id, sale_date, quantity, price, discount |
| inventory | one product/store/day | snapshot_date + store_id + product_id | on_hand_qty, reorder_level |

Gold fact_sales is transaction-line grain. Daily store sales is one row per date and store. Stock reorder alerts contain inventory rows at or below their reorder level.
