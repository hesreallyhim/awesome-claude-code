# Feature Engineering & Feature Store Guide

## Overview
Databricks Feature Engineering provides a centralized repository for features with automatic lineage, point-in-time lookups, and seamless integration with MLflow for training and inference.

## Build & Test Commands
- Install: `pip install databricks-feature-engineering`
- Run tests: `pytest tests/features/ -v`
- Validate feature table: `databricks feature-tables get <table_name>`

## Feature Engineering Client Setup

```python
from databricks.feature_engineering import FeatureEngineeringClient, FeatureLookup

fe = FeatureEngineeringClient()
```

## Creating Feature Tables

### From Spark DataFrame
```python
from pyspark.sql import functions as F

# Compute features
customer_features = (
    transactions_df
    .groupBy("customer_id")
    .agg(
        F.count("*").alias("transaction_count"),
        F.avg("amount").alias("avg_transaction_amount"),
        F.stddev("amount").alias("std_transaction_amount"),
        F.max("amount").alias("max_transaction_amount"),
        F.datediff(F.current_date(), F.max("transaction_date")).alias("days_since_last_txn")
    )
)

# Create feature table in Unity Catalog
fe.create_table(
    name="ml_prod.fraud_detection.customer_features",
    primary_keys=["customer_id"],
    df=customer_features,
    description="Customer transaction aggregation features",
    tags={"team": "fraud-ml", "refresh": "daily"}
)
```

### With Timestamp Key (Time-Series Features)
```python
# Features that change over time need a timestamp key
daily_features = (
    transactions_df
    .groupBy("customer_id", F.to_date("transaction_date").alias("feature_date"))
    .agg(
        F.sum("amount").alias("daily_spend"),
        F.count("*").alias("daily_txn_count")
    )
)

fe.create_table(
    name="ml_prod.fraud_detection.customer_daily_features",
    primary_keys=["customer_id"],
    timestamp_keys=["feature_date"],  # Enables point-in-time lookups
    df=daily_features,
    description="Daily customer spending features"
)
```

## Writing Features

### Batch Updates
```python
# Overwrite entire table
fe.write_table(
    name="ml_prod.fraud_detection.customer_features",
    df=new_features_df,
    mode="overwrite"
)

# Merge/upsert (update existing, insert new)
fe.write_table(
    name="ml_prod.fraud_detection.customer_features",
    df=updated_features_df,
    mode="merge"
)
```

### Streaming Updates
```python
def update_features_streaming(batch_df, batch_id):
    fe.write_table(
        name="ml_prod.fraud_detection.customer_features",
        df=batch_df,
        mode="merge"
    )

# Stream from Kafka/Event Hub
(spark
    .readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("subscribe", "transactions")
    .load()
    .select(parse_transaction("value").alias("txn"))
    .select("txn.*")
    .writeStream
    .foreachBatch(update_features_streaming)
    .start()
)
```

## Creating Training Sets

### Basic Feature Lookup
```python
# Labels DataFrame with entity keys
labels_df = spark.table("ml_prod.fraud_detection.fraud_labels")
# Schema: customer_id, transaction_id, is_fraud, label_date

# Define feature lookups
feature_lookups = [
    FeatureLookup(
        table_name="ml_prod.fraud_detection.customer_features",
        lookup_key=["customer_id"],
        feature_names=["transaction_count", "avg_transaction_amount", "days_since_last_txn"]
    ),
    FeatureLookup(
        table_name="ml_prod.fraud_detection.merchant_features",
        lookup_key=["merchant_id"],
        feature_names=["merchant_risk_score", "merchant_category"]
    )
]

# Create training set
training_set = fe.create_training_set(
    df=labels_df,
    feature_lookups=feature_lookups,
    label="is_fraud",
    exclude_columns=["transaction_id"]  # Don't include in features
)

# Convert to Pandas for training
training_df = training_set.load_df().toPandas()
X = training_df.drop("is_fraud", axis=1)
y = training_df["is_fraud"]
```

### Point-in-Time Lookups (Preventing Data Leakage)
```python
# CRITICAL: Use timestamp_lookup_key to prevent future data leakage
feature_lookups = [
    FeatureLookup(
        table_name="ml_prod.fraud_detection.customer_daily_features",
        lookup_key=["customer_id"],
        timestamp_lookup_key="label_date",  # Only use features available at this time
        feature_names=["daily_spend", "daily_txn_count"]
    )
]

training_set = fe.create_training_set(
    df=labels_df,
    feature_lookups=feature_lookups,
    label="is_fraud"
)
```

## Training Models with Feature Store

### Log Model with Feature Metadata
```python
import mlflow
from sklearn.ensemble import RandomForestClassifier

mlflow.set_registry_uri("databricks-uc")

with mlflow.start_run():
    # Train model
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    # Log model with feature engineering client
    # This captures feature lineage automatically
    fe.log_model(
        model=model,
        artifact_path="model",
        flavor=mlflow.sklearn,
        training_set=training_set,
        registered_model_name="ml_prod.ml_models.fraud_detector"
    )
```

## Inference with Feature Lookup

### Batch Scoring
```python
# Load model (automatically knows which features to look up)
model_uri = "models:/ml_prod.ml_models.fraud_detector@champion"

# Score with automatic feature lookup
# Only need to provide primary keys - features are looked up automatically
new_data = spark.createDataFrame([
    {"customer_id": "C001", "merchant_id": "M123"},
    {"customer_id": "C002", "merchant_id": "M456"}
])

predictions = fe.score_batch(
    model_uri=model_uri,
    df=new_data
)
predictions.show()
```

### Real-Time Serving
```python
# When model is deployed to serving endpoint, feature lookups happen automatically
# The endpoint fetches features from online tables

# Create online table for low-latency lookups
spark.sql("""
    CREATE ONLINE TABLE ml_prod.fraud_detection.customer_features_online
    TBLPROPERTIES (
        'source' = 'ml_prod.fraud_detection.customer_features',
        'primaryKey' = 'customer_id'
    )
""")
```

## On-Demand Features (Feature Functions)

### Define Feature Function
```python
from databricks.feature_engineering import FeatureFunction

# Register a feature function for real-time computation
@feature_function(
    name="ml_prod.fraud_detection.compute_velocity",
    input_bindings={"amount": "transaction_amount", "minutes": "time_window"}
)
def compute_velocity(amount: float, minutes: int) -> float:
    """Compute transaction velocity (amount per minute)."""
    return amount / max(minutes, 1)
```

### Use in Feature Lookup
```python
from databricks.feature_engineering import FeatureFunction

feature_lookups = [
    FeatureLookup(
        table_name="ml_prod.fraud_detection.customer_features",
        lookup_key=["customer_id"]
    ),
    FeatureFunction(
        udf_name="ml_prod.fraud_detection.compute_velocity",
        input_bindings={"amount": "transaction_amount", "minutes": "minutes_since_last"},
        output_name="transaction_velocity"
    )
]
```

## Feature Table Management

### Update Schema
```python
# Add new feature column
fe.write_table(
    name="ml_prod.fraud_detection.customer_features",
    df=features_with_new_column,
    mode="merge"
)

# The new column is automatically added to the schema
```

### Delete Feature Table
```python
# Soft delete (can be restored)
fe.drop_table(name="ml_prod.fraud_detection.customer_features")

# To permanently delete, use SQL
spark.sql("DROP TABLE ml_prod.fraud_detection.customer_features")
```

## Feature Freshness & Monitoring

### Check Feature Freshness
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Get table info including last update time
table_info = w.tables.get("ml_prod.fraud_detection.customer_features")
print(f"Last updated: {table_info.updated_at}")

# Monitor feature drift
feature_stats = spark.sql("""
    SELECT
        mean(transaction_count) as mean_txn_count,
        stddev(transaction_count) as std_txn_count,
        percentile(avg_transaction_amount, 0.5) as median_amount
    FROM ml_prod.fraud_detection.customer_features
""").collect()[0]
```

### Feature Validation
```python
from great_expectations.dataset import SparkDFDataset

def validate_features(df):
    ge_df = SparkDFDataset(df)

    # Validate feature ranges
    assert ge_df.expect_column_values_to_be_between(
        "transaction_count", min_value=0, max_value=10000
    ).success

    assert ge_df.expect_column_values_to_not_be_null(
        "customer_id"
    ).success

    return True
```

## Common Patterns

### Aggregation Windows
```python
from pyspark.sql import Window

# Rolling window features
window_7d = Window.partitionBy("customer_id").orderBy("date").rowsBetween(-6, 0)
window_30d = Window.partitionBy("customer_id").orderBy("date").rowsBetween(-29, 0)

features = (df
    .withColumn("txn_count_7d", F.count("*").over(window_7d))
    .withColumn("txn_count_30d", F.count("*").over(window_30d))
    .withColumn("avg_amount_7d", F.avg("amount").over(window_7d))
    .withColumn("avg_amount_30d", F.avg("amount").over(window_30d))
)
```

### Categorical Encoding
```python
from pyspark.ml.feature import StringIndexer, OneHotEncoder

# Create encoded features
indexer = StringIndexer(inputCol="merchant_category", outputCol="category_index")
encoder = OneHotEncoder(inputCol="category_index", outputCol="category_encoded")

# Fit and transform
indexed = indexer.fit(df).transform(df)
encoded = encoder.fit(indexed).transform(indexed)
```

## Best Practices

1. **Primary Keys**: Always define appropriate primary keys for efficient lookups
2. **Timestamp Keys**: Use for time-series features to enable point-in-time correctness
3. **Feature Naming**: Use descriptive names: `{entity}_{aggregation}_{window}`
4. **Documentation**: Add descriptions and tags to all feature tables
5. **Versioning**: Use separate tables or schemas for breaking changes
6. **Monitoring**: Set up alerts for feature freshness and drift

## Key Links
- Feature Engineering Guide: https://docs.databricks.com/en/machine-learning/feature-store/
- FeatureLookup API: https://docs.databricks.com/en/machine-learning/feature-store/train-models-with-feature-store.html
- Online Tables: https://docs.databricks.com/en/machine-learning/feature-store/online-tables.html
