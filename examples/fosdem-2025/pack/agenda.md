# FOSDEM 2025 · personal preparation pack

Data engineer: improve a Python analytics pipeline using columnar interchange, lakehouse formats, metadata checks and reliable orchestration, while protecting development data.

Display timezone: Europe/Madrid. Conference timezone: Europe/Brussels.
Historical FOSDEM 2025 replay with a synthetic attendee brief. The attendee knows basic table formats, requires dbt-score and PyArrow, leaves Sunday at 16:00, and wants no more than four sessions per day. Room-change allowance is not a measured walking route.

## Attendance and protected time

- 2025-02-01: 10:30–18:00 (Europe/Brussels)
- 2025-02-02: 09:00–16:00 (Europe/Brussels)
- Lunch: 2025-02-01 12:15–13:00 (Europe/Brussels)
- Lunch: 2025-02-02 12:30–13:15 (Europe/Brussels)

## Your agenda

### Sat 01 Feb · 10:30–11:00 | What the Spec?!: New Features in Apache Iceberg™ Table Format V3
UB5.132 · Data Analytics · Danica Fine, Russell Spitzer
[Official session](https://fosdem.org/2025/schedule/event/fosdem-2025-4707-what-the-spec-new-features-in-apache-iceberg-table-format-v3/)

Frames schema evolution and change tracking for the attendee's move toward an open lakehouse, with concrete format-level questions.

Questions:
- Which row-lineage guarantees depend on the writer rather than the table format alone?
- How should an existing V2 table be tested before relying on a V3 feature?

Prepare: Review current schema-change and CDC requirements. This is a historical 2025 abstract; do not use it as current release-status documentation.

Programme evidence: how Row Lineage can enhance CDC capabilities

Notes:


### Sat 01 Feb · 13:50–14:20 | ODBC Takes an Arrow to the Knee
UB5.132 · Data Analytics · Matthew Topol
[Official session](https://fosdem.org/2025/schedule/event/fosdem-2025-4803-odbc-takes-an-arrow-to-the-knee/)

Directly addresses the row-to-column conversion work at the boundary between databases and the attendee's Python analytics.

Questions:
- Which database-to-Python paths still copy or convert data even through ADBC?
- How do driver type mappings handle decimals, timestamps and nulls?

Prepare: Draw one current SQL-to-dataframe path and mark serialization, transposition and memory ownership boundaries.

Programme evidence: fetch result sets in the Arrow format

Notes:


### Sat 01 Feb · 16:05–16:35 | dbt-score: a linter for your dbt model metadata
UB5.132 · Data Analytics · Jochem van Dooren, Matthieu Caneill
[Official session](https://fosdem.org/2025/schedule/event/fosdem-2025-4335-dbt-score-a-linter-for-your-dbt-model-metadata/)

The mandatory metadata-quality session addresses repeatable documentation and contract checks across the attendee's data models.

Questions:
- How can rules be introduced without turning every existing model into a blocking CI failure?
- How do you distinguish metadata completeness from the correctness of the underlying data?

Prepare: Prepare two real categories of metadata rules to discuss: ownership and column documentation. The demo brief contains no private models.

Programme evidence: programmatically define and enforce metadata rules

Notes:


### Sat 01 Feb · 17:25–17:55 | Enhancing Airflow for Analytics, Data Engineering, and ML at Wikimedia
UB5.132 · Data Analytics · Ben Tullis, Balthazar Rouberol
[Official session](https://fosdem.org/2025/schedule/event/fosdem-2025-4867-enhancing-airflow-for-analytics-data-engineering-and-ml-at-wikimedia/)

Connects orchestration and infrastructure changes to operating real data pipelines, complementing the format and metadata talks.

Questions:
- Which migration checks caught failures that did not appear in isolated DAG tests?
- How are storage credentials and task retries handled across these components?

Prepare: Sketch the handoffs between orchestrator, execution engine and storage. Capture migration sequencing and failure recovery lessons.

Programme evidence: integration between Airflow, Kubernetes, Spark, and Ceph

Notes:


### Sun 02 Feb · 09:00–09:50 | PostgreSQL Performance - 20 years of improvements
UA2.220 (Guillissen) · PostgreSQL · Tomas Vondra
[Official session](https://fosdem.org/2025/schedule/event/fosdem-2025-4615-postgresql-performance-20-years-of-improvements/)

Provides a historical benchmark perspective so database upgrades are evaluated against workloads rather than feature lists.

Questions:
- How did you keep benchmark comparisons meaningful across hardware and release-era changes?
- Which workload characteristics should an analytics team preserve in its own upgrade benchmark?

Prepare: Bring a benchmark design with query mix, data size and cache-state controls; the talk is historical, not a recommendation for a current server version.

Programme evidence: basic benchmarks (both OLTP and OLAP)

Notes:


### Sun 02 Feb · 10:30–11:00 | FawltyDeps: Finding undeclared and unused dependencies in your notebooks and projects
UD2.218A · Python · Johan Herland
[Official session](https://fosdem.org/2025/schedule/event/fosdem-2025-5072-fawltydeps-finding-undeclared-and-unused-dependencies-in-your-notebooks-and-projects/)

Addresses a practical reproducibility failure in Python notebooks that feed the analytical pipeline.

Questions:
- How are optional imports and environment-specific dependencies classified?
- How can the check be integrated without silently removing dependencies used only at runtime?

Prepare: Compare imports, declared dependencies and environment exports for a small public notebook before applying a rule to a larger project.

Programme evidence: finds imports you forgot to declare

Notes:


### Sun 02 Feb · 11:00–11:30 | What can PyArrow do for you - Array interchange, storage, compute and transport
UD2.218A · Python · Rok Mihevc, Alenka Frim
[Official session](https://fosdem.org/2025/schedule/event/fosdem-2025-6092-what-can-pyarrow-do-for-you-array-interchange-storage-compute-and-transport/)

The mandatory Sunday session connects array interchange, file storage and transport within one Python data path.

Questions:
- Which dtype and nullability combinations prevent a zero-copy interchange?
- When should Arrow Flight replace a file-based boundary between two processing stages?

Prepare: Map the same SQL-to-dataframe path used for ADBC, adding the downstream serialization and transport boundaries.

Programme evidence: Array Interchange: Seamless data exchange between NumPy, pandas, and other libraries using zero-copy

Notes:


### Sun 02 Feb · 15:00–15:50 | PostgreSQL Anonymizer and the battle for privacy
UA2.220 (Guillissen) · PostgreSQL · Damien Clochard
[Official session](https://fosdem.org/2025/schedule/event/fosdem-2025-4258-postgresql-anonymizer-and-the-battle-for-privacy/)

Adds an explicit privacy step when analytical datasets are copied to development or shared with collaborators.

Questions:
- How can masking preserve analytical relationships without retaining re-identification paths?
- What tests reveal that a supposedly anonymized dump still contains sensitive combinations?

Prepare: List data relationships and invariants that a development copy must preserve. Treat masking as one control, not a proof of anonymity.

Programme evidence: Generating anonymized dumps for development environments

Notes:


## Alternatives and tradeoffs

- [Tuning Postgres for Analytics](https://fosdem.org/2025/schedule/event/fosdem-2025-5242-tuning-postgres-for-analytics/) · Sun 02 Feb · 11:00–11:50 · UA2.220 (Guillissen) · 5/5
  Time / room-change conflict. Conflicts with: FawltyDeps: Finding undeclared and unused dependencies in your notebooks and projects, What can PyArrow do for you - Array interchange, storage, compute and transport. Highly relevant to mixing analytics with application traffic, but it conflicts with the attendee's required PyArrow session.
- [[REPLACEMENT] Take the Polar Plunge: A Fearless Introduction to Apache Iceberg™](https://fosdem.org/2025/schedule/event/fosdem-2025-4701--replacement-take-the-polar-plunge-a-fearless-introduction-to-apache-iceberg-/) · Sat 01 Feb · 12:30–13:00 · UB5.132 · 4/5
  Overlaps Lunch. Useful lakehouse foundations, but the session overlaps the protected lunch and the attendee already knows basic table formats.
- [How we built a new powerful JSON data type for ClickHouse](https://fosdem.org/2025/schedule/event/fosdem-2025-6351-how-we-built-a-new-powerful-json-data-type-for-clickhouse/) · Sat 01 Feb · 14:45–15:15 · UB5.132 · 4/5
  Lower total priority under session cap. Relevant to semi-structured ingestion and schema drift, but lower priority than the four selected pipeline and interchange sessions.
- [Empowering Data Analytics: High-Performance Graph Queries in DuckDB with DuckPGQ](https://fosdem.org/2025/schedule/event/fosdem-2025-4135-empowering-data-analytics-high-performance-graph-queries-in-duckdb-with-duckpgq/) · Sat 01 Feb · 11:50–12:20 · UB5.132 · 3/5
  Overlaps Lunch. Shows when relational tables can support graph questions without a separate database, but graph workloads are optional for this brief.
- [Accelerating QuestDB: Lessons from a 6x Query Performance Boost](https://fosdem.org/2025/schedule/event/fosdem-2025-5214-accelerating-questdb-lessons-from-a-6x-query-performance-boost/) · Sat 01 Feb · 13:10–13:40 · UB5.132 · 3/5
  Lower total priority under session cap. Adds an implementation-level account of analytical performance, secondary to interchange and pipeline reliability.
- [Open Source Business Intelligence - Introduction to Apache Superset](https://fosdem.org/2025/schedule/event/fosdem-2025-4652-open-source-business-intelligence-introduction-to-apache-superset/) · Sat 01 Feb · 16:45–17:15 · UB5.132 · 3/5
  Lower total priority under session cap. A possible destination for the analytical results, but the current brief prioritizes getting data reliably into that destination.
- [Anatomy of Table-Level Locks in PostgreSQL](https://fosdem.org/2025/schedule/event/fosdem-2025-4603-anatomy-of-table-level-locks-in-postgresql/) · Sun 02 Feb · 13:00–13:50 · UA2.220 (Guillissen) · 3/5
  Overlaps Lunch. Useful for safe schema changes, but overlaps the protected Sunday lunch.
- [Effortless Distributed Computing in Python](https://fosdem.org/2025/schedule/event/fosdem-2025-4835-effortless-distributed-computing-in-python/) · Sun 02 Feb · 15:30–16:00 · UD2.218A · 3/5
  Time / room-change conflict. Conflicts with: PostgreSQL Anonymizer and the battle for privacy. An optional scaling path for Python jobs, but it overlaps the higher-priority privacy session.
- [Apache Arrow tensor arrays: an approach for storing tensor data](https://fosdem.org/2025/schedule/event/fosdem-2025-6096-apache-arrow-tensor-arrays-an-approach-for-storing-tensor-data/) · Sat 01 Feb · 14:30–14:35 · UB5.132 · 2/5
  Below minimum relevance score. A specialized tensor representation topic; this attendee mainly moves tabular analytical data.
- [Job-specific performance monitoring on HPC clusters: Challenges and Solutions](https://fosdem.org/2025/schedule/event/fosdem-2025-5831-job-specific-performance-monitoring-on-hpc-clusters-challenges-and-solutions/) · Sun 02 Feb · 16:30–16:55 · UB5.132 · 2/5
  Outside attendance window. An HPC monitoring alternative outside the Sunday departure window and secondary to this small analytics stack.

## Review and remaining work

Reviewed the complete 78-track inventory and title indexes for Data Analytics, Cloud Native Databases, PostgreSQL, MySQL, Python and HPC/Big Data. Read every Data Analytics abstract and the relevant Sunday Python/PostgreSQL/HPC abstracts. Prioritized interchange, metadata, orchestration, reproducibility and privacy over engine implementation, graph-specific visualization, tensor layouts and distributed-database architecture. Eighteen relevant or plausible alternatives received individual notes. No talk recordings or software performance claims were tested.

Review the subjective choices and the live official programme before attending. Room availability, accessibility and actual travel times are not verified. This is a snapshot, not a live calendar subscription. Importing ICS is optional; repeated imports may duplicate events. HTML scratchpad notes are not saved.
