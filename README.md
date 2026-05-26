# 🏎️ F1ow — F1 Data Pipeline

F1ow is an automated weekly Formula 1 data pipeline that fetches, stores, orchestrates, and analyzes race data using a medallion architecture on AWS.

## 🏗️ Architecture
![F1ow Architecture](assets/architecture.png)

### 🎭 Medallion Architecture
- **Bronze Layer** — Raw F1 JSON data ingested from Jolpica REST API
- **Silver Layer** — Cleaned and transformed data in Parquet format using Pandas
- **Gold Layer** — Aggregated business-ready driver and constructor performance metrics

## 🛠️ Tech Stack
- 🐍 **Python** — API ingestion, transformation and aggregation scripts
- ☁️ **AWS S3** — Cloud storage for medallion architecture (Bronze/Silver/Gold layers)
- 🔍 **AWS Glue** — Data cataloging via Glue Crawler for schema discovery
- 📊 **Amazon Athena** — Serverless SQL querying directly on S3 data
- 📦 **Apache Parquet** — Columnar storage format for Silver and Gold layers
- 🌬️ **Apache Airflow** — Orchestrates weekly pipeline runs via DAGs
- 🏗️ **Terraform** — Provisions AWS infrastructure as code
- 🐳 **Docker** — Containerizes and runs Airflow locally
- 🐙 **GitHub** — Version control and project tracking

## 📁 Project Structure
```plaintext
F1ow/
├── airflow/                  # Airflow DAGs and Docker setup
│   ├── dags/
│   │   └── f1ow_dag.py       # Pipeline DAG with 3 tasks
│   └── docker-compose.yaml
├── src/                      # Python scripts
│   ├── fetch_f1_data.py      # Ingestion — API to Bronze S3
│   ├── transform_f1_data.py  # Transformation — Bronze to Silver
│   └── aggregate_f1_data.py  # Aggregation — Silver to Gold
├── terraform/                # Infrastructure as code
│   └── main.tf
├── assets/                   # Project assets
│   └── architecture.png
└── README.md
```

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- Docker Desktop
- Terraform
- AWS Account with S3 and Glue access

### Steps
1. Clone the repository
```
git clone https://github.com/shams2808/F1ow.git
cd F1ow
```
2. Set up virtual environment
```
python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt
```
3. Configure AWS credentials
```
aws configure
```
4. Provision infrastructure
```
cd terraform
terraform init
terraform apply
```
5. Start Airflow
```
cd airflow
docker-compose up
```
6. Access Airflow UI at `http://localhost:8080` and trigger `f1ow_pipeline`

## 📊 Data Collected
- **Race Results** — All rounds for 2023, 2024 and 2025 seasons (70+ races)
- **Driver Standings** — Championship standings per season
- **Constructor Standings** — Team standings per season

## 🔍 Sample Athena Queries
```sql
-- Top drivers by wins in 2025
SELECT driver_name, total_wins, total_points
FROM driver_performance
WHERE season = 2025
ORDER BY total_wins DESC;

-- Verstappen performance across seasons
SELECT season, total_wins, total_points, podiums
FROM driver_performance
WHERE driverid = 'max_verstappen'
ORDER BY season;

-- Constructor championship comparison
SELECT constructor_name, season, total_points
FROM constructor_performance
ORDER BY season, total_points DESC;
```

## 🗺️ Roadmap
- [x] Phase 1 — Data ingestion pipeline with Airflow + AWS S3 + Terraform
- [x] Phase 2 — Medallion architecture + AWS Glue + Amazon Athena + Parquet
- [ ] Phase 3 — PySpark transformations + star schema modeling
- [ ] Phase 4 — Streamlit dashboard for F1 analytics