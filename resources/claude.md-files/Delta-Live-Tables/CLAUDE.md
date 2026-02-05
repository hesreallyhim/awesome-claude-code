# Delta Live Tables (DLT) Development Guide

## Overview
Delta Live Tables is a declarative ETL framework for building reliable data pipelines on Databricks. It handles orchestration, error handling, data quality, and automatic dependency management.

## Build & Test Commands
- Validate pipeline: `databricks pipelines validate`
- Start pipeline: `databricks pipelines start --pipeline-id <id>`
- Stop pipeline: `databricks pipelines stop --pipeline-id <id>`
- Get status: `databricks pipelines get --pipeline-id <id>`

## DLT Concepts

| Concept | Description |
|---------|-------------|
| **Pipeline** | A directed acyclic graph (DAG) of data transformations |
| **Table** | Materialized view that persists results to storage |
| **View** | Virtual table computed on-demand (not persisted) |
| **Streaming Table** | Incrementally processes new data as it arrives |
| **Expectations** | Data quality constraints that validate records |

## Pipeline Definition

### Basic Table
```python
import dlt
from pyspark.sql import functions as F

@dlt.table(
    name="bronze_events",
    comment="Raw events from source system",
    table_properties={"quality": "bronze"}
)
def bronze_events():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/mnt/data/events/")
    )
```

### Streaming Table with Schema
```python
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

schema = StructType([
    StructField("event_id", StringType(), False),
    StructField("user_id", StringType(), False),
    StructField("event_type", StringType(), True),
    StructField("timestamp", TimestampType(), False),
    StructField("properties", StringType(), True)
])

@dlt.table(
    name="bronze_events",
    comment="Raw events ingested via Auto Loader"
)
def bronze_events():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", "/mnt/checkpoints/events_schema")
        .schema(schema)
        .load("s3://bucket/events/")
    )
```

### Silver Layer Transformation
```python
@dlt.table(
    name="silver_events",
    comment="Cleaned and validated events"
)
@dlt.expect_or_drop("valid_user_id", "user_id IS NOT NULL")
@dlt.expect_or_drop("valid_timestamp", "timestamp > '2020-01-01'")
def silver_events():
    return (
        dlt.read_stream("bronze_events")
        .withColumn("event_date", F.to_date("timestamp"))
        .withColumn("properties_parsed", F.from_json("properties", properties_schema))
        .select(
            "event_id",
            "user_id",
            "event_type",
            "timestamp",
            "event_date",
            "properties_parsed.*"
        )
    )
```

### Gold Layer Aggregation
```python
@dlt.table(
    name="gold_daily_metrics",
    comment="Daily aggregated metrics"
)
def gold_daily_metrics():
    return (
        dlt.read("silver_events")
        .groupBy("event_date", "event_type")
        .agg(
            F.count("*").alias("event_count"),
            F.countDistinct("user_id").alias("unique_users"),
            F.avg("duration").alias("avg_duration")
        )
    )
```

## Data Quality with Expectations

### Expectation Types
```python
# Drop invalid records
@dlt.expect_or_drop("positive_amount", "amount > 0")

# Fail pipeline if constraint violated
@dlt.expect_or_fail("valid_id", "id IS NOT NULL")

# Track violations but keep records (default)
@dlt.expect("valid_email", "email LIKE '%@%'")

# Multiple expectations
@dlt.expect_all({
    "valid_user": "user_id IS NOT NULL",
    "valid_amount": "amount > 0",
    "valid_date": "transaction_date <= current_date()"
})

# Drop if any expectation fails
@dlt.expect_all_or_drop({
    "not_null_id": "id IS NOT NULL",
    "positive_value": "value >= 0"
})
```

### Complex Expectations
```python
@dlt.table(name="validated_transactions")
@dlt.expect_or_drop(
    "business_rule_1",
    """
    CASE 
        WHEN transaction_type = 'refund' THEN amount < 0
        WHEN transaction_type = 'purchase' THEN amount > 0
        ELSE TRUE
    END
    """
)
def validated_transactions():
    return dlt.read_stream("raw_transactions")
```

## Views vs Tables

### View (Not Materialized)
```python
@dlt.view(
    name="active_users_view",
    comment="Filter for active users - not persisted"
)
def active_users_view():
    return (
        dlt.read("users")
        .filter(F.col("status") == "active")
    )
```

### Temporary View for Intermediate Steps
```python
@dlt.view(name="_tmp_enriched_events")  # Prefix with _ for temporary
def tmp_enriched_events():
    events = dlt.read_stream("bronze_events")
    users = dlt.read("dim_users")
    return events.join(users, "user_id", "left")

@dlt.table(name="silver_enriched_events")
def silver_enriched_events():
    return dlt.read_stream("_tmp_enriched_events")
```

## Change Data Capture (CDC)

### Apply Changes for SCD Type 1
```python
dlt.create_streaming_table("customers_scd1")

dlt.apply_changes(
    target="customers_scd1",
    source="cdc_customers_raw",
    keys=["customer_id"],
    sequence_by="updated_at",
    stored_as_scd_type=1  # Overwrites with latest
)
```

### SCD Type 2 (History Tracking)
```python
dlt.create_streaming_table("customers_scd2")

dlt.apply_changes(
    target="customers_scd2",
    source="cdc_customers_raw",
    keys=["customer_id"],
    sequence_by="updated_at",
    stored_as_scd_type=2,  # Maintains history
    track_history_column_list=["name", "email", "address"]
)
```

### Handling Deletes
```python
dlt.apply_changes(
    target="products",
    source="cdc_products",
    keys=["product_id"],
    sequence_by="change_timestamp",
    apply_as_deletes=F.expr("operation = 'DELETE'"),
    apply_as_truncates=F.expr("operation = 'TRUNCATE'")
)
```

## Pipeline Configuration

### databricks.yml for Asset Bundles
```yaml
resources:
  pipelines:
    my_etl_pipeline:
      name: "My ETL Pipeline"
      target: "my_catalog.my_schema"
      
      libraries:
        - notebook:
            path: ./notebooks/bronze.py
        - notebook:
            path: ./notebooks/silver.py
        - notebook:
            path: ./notebooks/gold.py
      
      configuration:
        "spark.sql.shuffle.partitions": "auto"
        "pipelines.trigger.interval": "1 hour"
      
      clusters:
        - label: "default"
          autoscale:
            min_workers: 1
            max_workers: 4
          spark_conf:
            "spark.databricks.delta.preview.enabled": "true"
      
      continuous: false  # Triggered mode
      development: true  # Dev mode for faster iteration
      
      channel: "PREVIEW"  # or "CURRENT" for stable
```

### Pipeline Settings
```python
# In notebook, access pipeline settings
spark.conf.get("pipelines.trigger.interval")

# Environment-specific configuration
import os
env = os.getenv("ENVIRONMENT", "dev")
source_path = f"/mnt/{env}/data/"
```

## Streaming vs Batch

### Streaming Table (Incremental)
```python
@dlt.table(name="streaming_events")
def streaming_events():
    # Processes only new files incrementally
    return (
        spark.readStream
        .format("cloudFiles")
        .load("/data/events/")
    )
```

### Batch Table (Full Refresh)
```python
@dlt.table(name="batch_snapshot")
def batch_snapshot():
    # Reprocesses all data on each run
    return spark.read.format("delta").load("/data/snapshot/")
```

### Mixed Mode
```python
@dlt.table(name="enriched_events")
def enriched_events():
    # Streaming source
    events = dlt.read_stream("streaming_events")
    # Batch dimension (automatically handles stream-static join)
    products = dlt.read("dim_products")
    
    return events.join(products, "product_id", "left")
```

## Medallion Architecture Pattern

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   BRONZE    │───▶│   SILVER    │───▶│    GOLD     │
│  Raw Data   │    │  Cleaned    │    │ Aggregated  │
│  As-Is     │    │  Validated  │    │  Business   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Complete Pipeline Example
```python
import dlt
from pyspark.sql import functions as F

# ========== BRONZE ==========
@dlt.table(name="bronze_orders", table_properties={"quality": "bronze"})
def bronze_orders():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/data/orders/")
    )

@dlt.table(name="bronze_customers", table_properties={"quality": "bronze"})
def bronze_customers():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .load("/data/customers/")
    )

# ========== SILVER ==========
@dlt.table(name="silver_orders", table_properties={"quality": "silver"})
@dlt.expect_or_drop("valid_order_id", "order_id IS NOT NULL")
@dlt.expect_or_drop("positive_amount", "total_amount > 0")
def silver_orders():
    return (
        dlt.read_stream("bronze_orders")
        .withColumn("order_date", F.to_date("order_timestamp"))
        .withColumn("total_amount", F.col("total_amount").cast("decimal(10,2)"))
        .dropDuplicates(["order_id"])
    )

@dlt.table(name="silver_customers", table_properties={"quality": "silver"})
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
def silver_customers():
    return (
        dlt.read_stream("bronze_customers")
        .withColumn("full_name", F.concat("first_name", F.lit(" "), "last_name"))
        .dropDuplicates(["customer_id"])
    )

# ========== GOLD ==========
@dlt.table(name="gold_customer_orders", table_properties={"quality": "gold"})
def gold_customer_orders():
    orders = dlt.read("silver_orders")
    customers = dlt.read("silver_customers")
    
    return (
        orders.join(customers, "customer_id", "inner")
        .groupBy("customer_id", "full_name")
        .agg(
            F.count("order_id").alias("total_orders"),
            F.sum("total_amount").alias("lifetime_value"),
            F.max("order_date").alias("last_order_date")
        )
    )
```

## Monitoring and Debugging

### Event Log Queries
```sql
-- Pipeline run history
SELECT * FROM event_log(TABLE(my_catalog.my_schema.__apply_changes_storage))

-- Data quality metrics
SELECT
    expectations.name,
    expectations.passed_records,
    expectations.failed_records
FROM my_catalog.my_schema.__event_log
WHERE event_type = 'flow_progress'
```

### Lineage in Unity Catalog
```sql
-- View table lineage
SELECT * FROM system.access.table_lineage
WHERE target_table_name = 'gold_customer_orders'
```

## Best Practices

1. **Naming**: Use bronze/silver/gold prefixes for clarity
2. **Expectations**: Add data quality checks at silver layer
3. **Idempotency**: Design tables to handle re-runs safely
4. **Partitioning**: Partition large tables by date
5. **Checkpoints**: Let DLT manage checkpoints automatically
6. **Testing**: Use development mode for faster iteration
7. **Monitoring**: Check expectation metrics in pipeline UI

## Key Links
- Delta Live Tables: https://docs.databricks.com/en/delta-live-tables/
- DLT Python Reference: https://docs.databricks.com/en/delta-live-tables/python-ref.html
- Expectations: https://docs.databricks.com/en/delta-live-tables/expectations.html
