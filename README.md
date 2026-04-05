# 🏎️ F1ow — F1 Data Pipeline

F1ow is an automated weekly Formula 1 data pipeline that fetches, stores, and orchestrates race data for analysis.

## 🏗️ Architecture
![F1ow Architecture](assets/architecture.png)

## 🛠️ Tech Stack
- 🐍 **Python** — API ingestion scripts and boto3 for AWS interaction
- ☁️ **AWS S3** — Cloud storage for raw and processed data layers
- 🌬️ **Apache Airflow** — Orchestrates weekly pipeline runs via DAGs
- 🏗️ **Terraform** — Provisions AWS S3 infrastructure as code
- 🐳 **Docker** — Containerizes and runs Airflow locally
- 🐙 **GitHub** — Version control and project tracking

## 📁 Project Structure
F1ow/
├── airflow/          # Airflow DAGs and Docker setup
│   ├── dags/         # DAG definitions
│   ├── logs/         # Airflow logs
│   └── docker-compose.yaml
├── src/              # Python ingestion scripts
│   └── fetch_f1_data.py
├── terraform/        # Infrastructure as code
│   └── main.tf
├── assets/           # Project assets
│   └── architecture.png
└── README.md

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- Docker Desktop
- Terraform
- AWS Account with S3 access

### Steps
1. Clone the repository
git clone https://github.com/shams2808/F1ow.git
cd F1ow
2. Set up virtual environment
python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt
3. Configure AWS credentials
aws configure
4. Provision infrastructure
cd terraform
terraform init
terraform apply
5. Start Airflow
cd airflow
docker-compose up
6. Access Airflow UI at `http://localhost:8080` and trigger `f1ow_pipeline`

## 📊 Data Collected
- **Race Results** — All rounds for 2023, 2024 and 2025 seasons
- **Driver Standings** — Championship standings per season
- **Constructor Standings** — Team standings per season

## 🗺️ Roadmap
- [x] Phase 1 — Data ingestion pipeline with Airflow + AWS S3 + Terraform
- [ ] Phase 2 — AWS Glue data catalog + Iceberg data lakehouse
- [ ] Phase 3 — PySpark transformations + star schema modeling
- [ ] Phase 4 — Streamlit dashboard for F1 analytics
