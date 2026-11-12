-- Daily revenue and order volume
SELECT sale_date, store_id, COUNT(*) AS orders,
       SUM(quantity) AS units, SUM(net_sales) AS net_revenue
FROM retail_mart.fact_sales
GROUP BY sale_date, store_id
ORDER BY sale_date, store_id;

-- Category contribution
SELECT p.category, SUM(f.net_sales) AS revenue,
       ROUND(100.0 * SUM(f.net_sales) / SUM(SUM(f.net_sales)) OVER (), 2) AS revenue_pct
FROM retail_mart.fact_sales f
JOIN retail_mart.dim_product p USING (product_id)
GROUP BY p.category
ORDER BY revenue DESC;

-- Stockout risk can be joined to the Gold stock_reorder_alerts dataset.
