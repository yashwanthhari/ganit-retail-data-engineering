# Architecture and design

## Flow

1. **Source simulation:** daily CSV snapshots and transaction events are written to a date-stamped landing folder.
2. **Bronze:** preserve source columns and add ingestion timestamp/source filename. Bronze is the replayable raw layer.
3. **Silver:** cast business types, deduplicate business keys, validate mandatory fields and enforce reference integrity. Invalid facts are written to quarantine.
4. **Gold:** publish a sales fact, daily store KPI aggregate and low-stock/reorder alert dataset.
5. **Serving:** Gold can be loaded to PostgreSQL and explored in Metabase. MinIO provides an S3-compatible object store for raw/curated files.
6. **Orchestration:** Airflow runs source generation followed by ETL. In a real deployment, generation is replaced by source/API/SFTP ingestion.

## Idempotency and incremental processing

Each run writes to `run_date=YYYY-MM-DD`. The pipeline removes and recreates only that run-date output partition, so rerunning a failed date does not append duplicate rows. Sales retain their own `sale_id`; production CDC should use source offsets or an updated_at watermark and a merge/upsert strategy.

## CDC and SCD

The sample generator changes a small number of product/customer attributes on later dates. The starter silver layer takes one row per business key for the current snapshot. For full SCD Type 2, maintain a history table with:
- business key and surrogate key
- `effective_from`, `effective_to`
- `is_current`
- change hash

When tracked attributes change, expire the previous current row and insert a new current row. For SCD Type 1, update the current row in place. This is a documented extension, not falsely represented as already implemented.

## Production hardening backlog

- Persist ingestion manifests, row counts, checksums and watermarks.
- Use schema contracts and explicit schemas instead of inference.
- Route unmatched foreign keys to a separate quarantine reason.
- Add late-arrival lookback windows and deterministic merge keys.
- Add retry/backoff, alerting, secrets management and data lineage.
- Use a proper Airflow metadata database and a Spark cluster for larger workloads.
