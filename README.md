# Retail Data Engineering & Analytics Platform

A **Ganit-inspired, portfolio-grade retail ETL project** built entirely with free, open-source tools. This is an educational simulation of a retail analytics platform, not a copy of Ganit's internal systems or client data.

## What it demonstrates

- Multi-source batch ingestion (customers, products, stores, sales, inventory)
- Synthetic daily drops with inserts, updates and late-arriving sales
- PySpark transformations through Bronze → Silver → Gold (Parquet)
- Data quality checks, duplicate handling, referential integrity and quarantine
- Incremental processing by business date and repeatable/idempotent runs
- PostgreSQL analytical mart, with SQL for retail KPIs
- Local S3-compatible storage with MinIO
- Docker Compose services for PostgreSQL, MinIO, Airflow and Metabase
- Unit tests and an architecture suitable for interview discussion

## Free local stack

| Layer | Tool | Purpose |
|---|---|---|
| ETL | Python 3.11, PySpark 3.5 | Ingestion and transformations |
| Object storage | MinIO Community | S3-compatible raw/curated storage |
| Warehouse | PostgreSQL 16 | Analytics mart |
| Orchestration | Apache Airflow 2.10 | Scheduling and dependencies |
| BI | Metabase Community | Dashboards |
| Quality | pytest | Automated checks |

No AWS account, cloud credits, paid APIs or Databricks subscription are needed. AWS equivalents are documented for interview mapping only.

## Architecture

```text
Synthetic daily source drops (CSV)
          |
          v
     data/source/
          |
          v
  Bronze: immutable raw Parquet
          |
          v
  Silver: typed, deduplicated, validated
          |                           |                  -> quarantine/
          v
  Gold: fact_sales + dimensions + KPI aggregates
          |
          +----> PostgreSQL retail_mart
          |
          +----> MinIO bucket (optional archival)
          |
          v
      Metabase dashboards

Airflow orchestrates the daily pipeline; pytest validates core logic.
```

## Quick start (pipeline first)

Requirements: Ubuntu/WSL2 or Linux, Python 3.11, Java 11 or 17, Docker + Compose (optional for services).

```bash
git clone https://github.com/yashwanthhari/ganit-retail-data-engineering.git
cd ganit-retail-data-engineering
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
python -m src.generate_data --date 2026-01-01
python -m src.pipeline --date 2026-01-01
pytest -q
```

The pipeline creates local Parquet datasets under `data/lake/{bronze,silver,gold}`. It is safe to rerun the same date: that date's output partitions are replaced rather than duplicated.

Generate another day to simulate daily CDC changes:

```bash
python -m src.generate_data --date 2026-01-02
python -m src.pipeline --date 2026-01-02
```

The generator intentionally updates some product/customer records, adds new sales and includes a late-arriving sale. The current starter pipeline resolves the latest record per business key; the project docs describe how to extend this to full effective-dated SCD Type 2 history.

## Start local services

```bash
docker compose up -d
```

- MinIO console: http://localhost:9001 (minioadmin / minioadmin123)
- PostgreSQL: localhost:5432 (retail / retail)
- Airflow: http://localhost:8080 (admin / admin)
- Metabase: http://localhost:3000

Services are optional for running the local PySpark pipeline. Do not expose these development credentials to the internet.

## Project layout

```text
src/
  common/       configuration and helpers
  quality/      data quality rules
  generate_data.py
  pipeline.py   Bronze → Silver → Gold pipeline
sql/             warehouse DDL and KPI queries
dags/            Airflow DAG
tests/           unit tests
docs/            architecture, data model and interview notes
data/            generated input and local lake (gitignored)
```

## Data model and business questions

Gold outputs include sales facts and daily product/store performance. Example questions:
- What are daily and monthly net sales by store, category and region?
- Which products have high sales velocity but low available inventory?
- What is the return/discount rate by product category?
- Which stores have recurring stockouts?
- How do actual sales compare with inventory movement?

## Next milestones

1. Run the local pipeline and inspect Parquet outputs.
2. Start Docker services and load Gold outputs into PostgreSQL.
3. Add Airflow scheduling and Metabase dashboards.
4. Extend customer/store dimensions to full SCD Type 2 with `effective_from`, `effective_to`, `is_current`.
5. Add schema evolution, incremental watermarks, reconciliation and failure-recovery tests.

See [architecture](docs/architecture.md), [data dictionary](docs/data_dictionary.md), and [interview guide](docs/interview_guide.md).
