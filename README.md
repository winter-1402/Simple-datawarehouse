# NYC Taxi Data Pipeline with Apache Airflow

A complete data engineering project that orchestrates ETL (Extract, Transform, Load) workflows for processing NYC taxi trip data using **Apache Airflow**, **PostgreSQL**, and **MinIO** object storage.

## 📋 Project Overview

This project automates the entire data pipeline process:
- **Extract**: Downloads NYC taxi trip data (Yellow & Green taxis) from AWS and taxi zone lookup files
- **Transform**: Processes and cleans raw taxi data, merges datasets, and prepares for analysis
- **Load**: Stores processed data into PostgreSQL data warehouse with dimensional tables

The pipeline is orchestrated monthly using Airflow DAGs (Directed Acyclic Graphs) with LocalExecutor.

## 🏗️ Project Structure

```
.
├── dags/                              # Airflow DAGs
│   ├── dag_main.py                    # Main orchestration workflow
│   └── scripts/                       # Python scripts for data processing
│       ├── __init__.py
│       ├── download_data.py           # Download taxi data from AWS
│       ├── transform_data.py          # Transform and clean data
│       ├── load_data.py               # Load data to PostgreSQL
│       └── function_helper.py         # Helper functions for S3/MinIO operations
├── data/                              # Local data storage
│   ├── data_time.csv
│   ├── taxi_data_info.csv
│   ├── taxi_data_payment.csv
│   ├── taxi_data_time.csv
│   └── taxi_zone_lookup.csv
├── storage/                           # MinIO data storage (S3-like)
│   ├── data/                          # Processed data
│   ├── image/                         # Taxi zone maps
│   └── raw-data/                      # Raw downloaded taxi data
├── logs/                              # Airflow logs
├── plugins/                           # Airflow plugins (if needed)
├── docker-compose.yaml                # Docker services configuration
├── init.sql                           # Database initialization script
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- **Docker** & **Docker Compose** installed on your system
- At least 4GB of available RAM
- Stable internet connection (for downloading taxi data)

### Installation & Setup

1. **Clone/Navigate to the project directory:**
   ```bash
   cd /path/to/project
   ```

2. **Start all services using Docker Compose:**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database (port 5432)
   - Airflow webserver (port 8080)
   - Airflow scheduler
   - MinIO object storage (ports 9000, 9001)

3. **Wait for services to be ready:**
   ```bash
   # Check health of services
   docker-compose ps
   ```

4. **Access Airflow Web UI:**
   - Open: http://localhost:8080
   - Username: `airflow`
   - Password: `airflow`

5. **Access MinIO Console:**
   - Open: http://localhost:9001
   - Username: `system_user`
   - Password: `system_password`

### Database Access

Connect to PostgreSQL using any client:
- **Host**: localhost
- **Port**: 5432
- **Database**: airflow
- **Username**: airflow
- **Password**: airflow

Example with psql:
```bash
psql -h localhost -U airflow -d airflow
```

## 📊 Data Pipeline Workflow

The main DAG (`sequence_3_files`) executes three tasks in sequence:

### 1. **Extract (run_file_1)**
   - Downloads current month's NYC taxi trip data (Parquet format):
     - Yellow taxi trips: `yellow_tripdata_YYYY-MM.parquet`
     - Green taxi trips: `green_tripdata_YYYY-MM.parquet`
   - Falls back to previous months if current data unavailable
   - Downloads taxi zone lookup CSV
   - Downloads taxi zone map images (Brooklyn, Manhattan, Queens, Staten Island)
   - Stores files in MinIO buckets: `raw-data`, `data`, `image`

### 2. **Transform (run_file_2)**
   - Processes and cleans raw taxi data
   - Computes derived fields and aggregations
   - Prepares data for loading

### 3. **Load (run_file_3)**
   - Loads transformed data into PostgreSQL dimensional tables
   - Creates/updates fact and dimension tables

## 📅 DAG Schedule

- **DAG ID**: `sequence_3_files`
- **Schedule**: Monthly at 00:00 on the 1st day of each month (`0 0 1 * *`)
- **Start Date**: June 1, 2026
- **Catchup**: Disabled (won't backfill past runs)

## 🗄️ Database Schema

The PostgreSQL database includes dimensional tables for data warehousing:

### Dimension Tables
- `dim_location` - Taxi zones and boroughs
- `dim_vendor` - Taxi vendor information
- `dim_ratecode` - Rate code descriptions
- `dim_payment_type` - Payment method types
- `dim_trip_type` - Trip type information
- `dim_type` - Type classifications
- `dim_date` - Date dimension

These are pre-populated with lookup data during initialization (see `init.sql`).

## 🔧 Configuration

### Environment Variables (docker-compose.yaml)

```yaml
AIRFLOW__CORE__EXECUTOR: LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
AIRFLOW__CORE__FERNET_KEY: 46BKJoQYlPPOexq0OhDZnIlNepKFf87WFwLbfzqDDho=
AIRFLOW__CORE__LOAD_EXAMPLES: false
```

### MinIO Configuration
- **Root User**: system_user
- **Root Password**: system_password
- **Buckets**: raw-data, data, image

## 📝 Data Sources

The pipeline uses data from:
- **NYC Taxi & Limousine Commission (TLC)**
  - Yellow Taxi trip data: `https://d37ci6vzurychx.cloudfront.net/trip-data/`
  - Green Taxi trip data: `https://d37ci6vzurychx.cloudfront.net/trip-data/`
  - Taxi Zone Lookup: `https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv`
- **NYC Government**
  - Taxi zone maps: `https://www.nyc.gov/assets/tlc/images/content/pages/about/`

## 🛠️ Common Commands

### View Logs
```bash
# Scheduler logs
docker-compose logs -f airflow-scheduler

# Webserver logs
docker-compose logs -f airflow-webserver

# View last 100 lines
docker-compose logs --tail=100 airflow-scheduler
```

### Execute DAG Manually
```bash
# Trigger the DAG from Airflow UI
# Or via CLI:
docker-compose exec airflow-scheduler airflow dags test sequence_3_files 2026-05-01
```

### Stop Services
```bash
docker-compose down
```

### Clean Up Everything (including volumes)
```bash
docker-compose down -v
```

## 📦 Key Technologies

| Technology | Purpose | Version |
|-----------|---------|---------|
| Apache Airflow | Workflow orchestration | 2.8.1 |
| PostgreSQL | Data warehouse | 13 |
| MinIO | S3-compatible object storage | Latest |
| Python | Data processing scripts | 3.x |
| Docker | Containerization | Latest |

## 🚨 Troubleshooting

### Services won't start
```bash
# Check Docker daemon is running
docker ps

# View service logs
docker-compose logs

# Rebuild containers
docker-compose up --build
```

### Airflow webserver unreachable
```bash
# Wait for initialization (may take 2-3 minutes)
docker-compose logs airflow-init

# Check webserver health
docker-compose exec airflow-webserver curl http://localhost:8080/health
```

### Database connection errors
```bash
# Verify PostgreSQL is running
docker-compose exec postgres pg_isready

# Check database exists
docker-compose exec postgres psql -U airflow -l
```

### Data download failures
- Check internet connectivity
- Verify AWS S3 endpoint is accessible
- Check logs in `logs/scheduler/` directory

## 📊 Monitoring

### Airflow Metrics
- Access admin panel at http://localhost:8080/admin
- Monitor DAG runs, task success/failure rates
- View logs for each task execution

### MinIO Storage
- Monitor storage usage at http://localhost:9001
- Check bucket contents and file sizes

### PostgreSQL Queries
```sql
-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname != 'pg_catalog' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 📖 Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [NYC TLC Data Dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf)
- [MinIO Documentation](https://docs.min.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 📝 Notes

- The pipeline is configured with **LocalExecutor** for single-machine deployment
- For production, consider upgrading to **CeleryExecutor** or **KubernetesExecutor**
- Ensure sufficient disk space for raw data storage (~1-2GB per month)
- The Fernet key in docker-compose.yaml should be changed for production use

## 🤝 Contributing

For modifications or improvements:
1. Update relevant scripts in `dags/scripts/`
2. Modify DAG logic in `dags/dag_main.py`
3. Update `init.sql` if database schema changes
4. Test locally before deployment

## 📄 License

[Add your license information here]

---

**Last Updated**: May 3, 2026
