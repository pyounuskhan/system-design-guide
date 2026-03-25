# Analytics & Data Platforms — Glossary

| Term | Definition |
|------|-----------|
| **Event** | A single recorded user or system action (e.g., "product.viewed", "order.placed") |
| **Clickstream** | The sequence of user interactions within a session |
| **Session** | A group of user events bounded by inactivity gap (typically 30 minutes) |
| **Sessionization** | The process of grouping raw events into sessions |
| **Schema Registry** | Service that validates and evolves event schemas (Avro/JSON Schema) |
| **Watermark** | In stream processing, the point in event time below which all events are expected to have arrived |
| **Late-Arriving Event** | An event that arrives after its watermark has passed |
| **Grace Period** | Time window after watermark allowing late events to still be processed |
| **Exactly-Once** | Processing guarantee where each event affects output exactly once, despite failures |
| **At-Least-Once** | Events processed one or more times; consumers must handle duplicates |
| **Checkpointing** | Periodic snapshot of processing state for failure recovery (Flink/Spark) |
| **ETL** | Extract, Transform, Load — pipeline pattern for data movement |
| **ELT** | Extract, Load, Transform — load raw data first, transform in warehouse |
| **Data Lake** | Storage layer (S3/GCS) holding raw and processed data in open formats |
| **Data Warehouse** | Analytical database optimized for SQL queries on structured data |
| **OLAP** | Online Analytical Processing — sub-second aggregation queries |
| **OLTP** | Online Transaction Processing — fast row-level reads/writes (production databases) |
| **Star Schema** | Data model with a central fact table surrounded by dimension tables |
| **Fact Table** | Table recording measurable events (orders, clicks, transactions) |
| **Dimension Table** | Table describing attributes of entities (users, products, dates) |
| **SCD** | Slowly Changing Dimension — tracking historical changes in dimension attributes |
| **Columnar Storage** | Storing data by column rather than row; enables fast analytical queries and compression |
| **Parquet** | Open-source columnar storage format widely used in data lakes |
| **Apache Iceberg** | Table format providing ACID transactions, schema evolution, time travel on data lakes |
| **Delta Lake** | Databricks' table format with ACID transactions on data lakes |
| **MergeTree** | ClickHouse's primary table engine with sorted storage and background merges |
| **DAG** | Directed Acyclic Graph — workflow representation in Airflow |
| **Feature Store** | Centralized repository for ML features serving training and inference |
| **Training-Serving Skew** | Difference in feature computation between training and inference environments |
| **Feature Freshness** | How recently a feature was computed/updated in the online store |
| **A/B Test** | Controlled experiment comparing two variants with random user assignment |
| **Guardrail Metric** | Metric that must not degrade during an experiment, regardless of primary outcome |
| **Statistical Significance** | Confidence that observed difference is not due to random chance (typically p < 0.05) |
| **Sample Ratio Mismatch (SRM)** | When experiment groups have unequal sizes, indicating assignment bias |
| **Orthogonal Assignment** | Running multiple experiments independently on the same users without interaction |
| **Data Lineage** | Tracking how data flows from source through transformations to final output |
| **Data Quality** | Accuracy, completeness, freshness, and consistency of data |
| **CDC** | Change Data Capture — streaming database changes as events |
| **Flink** | Apache Flink — distributed stream processing framework |
| **Spark** | Apache Spark — distributed batch processing framework |
| **Airflow** | Apache Airflow — workflow orchestration for ETL pipelines |
| **ClickHouse** | Column-oriented OLAP database for real-time analytics |
| **Druid** | Apache Druid — real-time OLAP database for event-driven data |
| **Kafka** | Apache Kafka — distributed event streaming platform |
