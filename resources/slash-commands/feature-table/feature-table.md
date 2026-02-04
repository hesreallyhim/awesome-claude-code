# Claude Command: Feature Table

Create and manage feature tables in Databricks Feature Store with Unity Catalog.

## Usage

```
/feature-table
/feature-table --name catalog.schema.features
/feature-table --primary-key customer_id
```

## What This Command Does

1. Creates feature table schema in Unity Catalog
2. Generates feature computation code
3. Sets up primary and timestamp keys
4. Creates feature lookup configurations

## Creating Feature Tables

```python
from databricks.feature_engineering import FeatureEngineeringClient

fe = FeatureEngineeringClient()

fe.create_table(
    name="ml_prod.project.customer_features",
    primary_keys=["customer_id"],
    df=features_df,
    description="Customer transaction features"
)
```

## With Timestamp Key (Point-in-Time)

```python
fe.create_table(
    name="ml_prod.project.time_features",
    primary_keys=["customer_id"],
    timestamp_keys=["feature_timestamp"],
    df=features_df
)
```

## Feature Lookups for Training

```python
from databricks.feature_engineering import FeatureLookup

feature_lookups = [
    FeatureLookup(
        table_name="ml_prod.project.customer_features",
        lookup_key="customer_id",
        feature_names=["feature1", "feature2"]
    )
]

training_set = fe.create_training_set(
    df=labels_df,
    feature_lookups=feature_lookups,
    label="target"
)
```

## Best Practices

- Always define primary keys for joins
- Use timestamp keys for time-series features
- Document features with descriptions
- Validate data quality before writing
