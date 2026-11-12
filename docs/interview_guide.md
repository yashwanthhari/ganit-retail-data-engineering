# Interview talking points

**Business problem:** Retail leadership needs consistent visibility into sales, product performance and inventory risk across stores.

**Why medallion?** Bronze preserves replayable source data; Silver standardizes and validates; Gold exposes business-ready facts and aggregates.

**Why PySpark?** It offers distributed DataFrame transformations and scales the same logical pipeline beyond a laptop. This demo uses local mode to stay free.

**How is rerun safety achieved?** Output is partitioned by processing date and that partition is replaced on rerun. A production implementation would persist a batch manifest and merge on stable business keys.

**How is data quality handled?** Mandatory-field and quantity/price rules split bad records into quarantine; dimension joins enforce reference integrity; uniqueness is asserted on sale_id.

**CDC vs SCD:** CDC describes capturing source changes. SCD describes how dimensional history is stored. The generator simulates changed reference attributes; full SCD2 history is a planned extension documented in architecture.md.

**Cloud mapping (conceptual only):** MinIO → Amazon S3; Airflow → MWAA or self-managed Airflow; PostgreSQL mart → Redshift (not a one-to-one replacement); local Spark → EMR/Glue/Databricks. These cloud services are not used by this free project.

Be transparent in interviews: describe this as a self-built simulated retail pipeline, not production experience at Ganit or access to Ganit's proprietary architecture.
