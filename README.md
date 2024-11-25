# 🚀 Hackathon Pipeline Airflow

A robust ETL pipeline built with Apache Airflow to scrape, process, and store hackathon data from Devpost and Major League Hacking (MLH) platforms.

## 🎯 Overview

This project implements an automated data pipeline that:
- 🔍 Scrapes hackathon listings from Devpost's API and MLH's website
- 🔄 Processes and standardizes the data
- ☁️ Stores the results in AWS S3
- ⏰ Runs on a daily schedule using Apache Airflow

## 🏗️ Architecture

The pipeline consists of three main components:
1. 🌐 Devpost Scraper: Fetches hackathon data from Devpost's API
2. 🌍 MLH Scraper: Scrapes hackathon information from MLH's website
3. 🔧 Data Processor: Combines and cleans the data from both sources

## 📋 Prerequisites

- 🐳 Docker and Docker Compose
- 🐍 Python 3.8+
- ☁️ AWS Account with S3 access
- 🌬️ Apache Airflow 2.5.0
- 🛠️ Astronomer CLI

## 📁 Project Structure

```
hackathon_pipeline_airflow/
├── dags/
│   └── hackathon_etl_dag.py    # Main Airflow DAG file
│   └── scrape_devpost.py       # Standalone Devpost scraper
│   └── scrape_mlh.py           # Standalone MLH scraper
├── docker-compose.yaml          # Docker configuration
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## 🚀 Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hackathon_pipeline_airflow
```

2. Configure AWS credentials:
   - ✨ Set up an AWS S3 bucket
   - 🔑 Create an Airflow connection for AWS credentials in the Airflow UI:
     - Conn Id: `aws_s3`
     - Conn Type: `Amazon Web Services`
     - Login: AWS access key ID
     - Password: AWS secret access key
     - Extra: `{"region_name": "ap-south-1"}`

3. Start Airflow using Astro CLI:
```bash
astro dev start
```

This command will spin up 4 Docker containers on your machine:
- 📊 Postgres: Airflow's Metadata Database
- 🖥️ Webserver: The Airflow component for rendering the Airflow UI
- ⚙️ Scheduler: The Airflow component for monitoring and triggering tasks
- 🔄 Triggerer: The Airflow component for triggering deferred tasks

4. Verify the containers:
```bash
docker ps
```

5. Access the Airflow UI:
   - 🌐 URL: `http://localhost:8080`
   - 👤 Username: `admin`
   - 🔒 Password: `admin`

Note: If ports 8080 (Webserver) or 5432 (Postgres) are already in use, you can either stop existing Docker containers or change the ports following [Astronomer's documentation](https://www.astronomer.io/docs/astro/cli/troubleshoot-locally#ports-are-not-available-for-my-local-airflow-webserver).

## ⚙️ DAG Configuration

The main DAG (`hackathon_etl_dag.py`) runs daily and consists of three tasks:
1. 🌐 `scrape_devpost`: Fetches data from Devpost API
2. 🌍 `scrape_mlh`: Scrapes data from MLH website
3. 🔄 `combine_and_clean`: Merges and processes data from both sources

## 💾 Data Storage

The pipeline stores data in three S3 files:
- 📁 `devpost.csv`: Raw data from Devpost
- 📁 `mlh.csv`: Raw data from MLH
- 📁 `combined.csv`: Processed and cleaned data from both sources

## 👩‍💻 Development

To run the scrapers independently of Airflow:

```bash
# Run Devpost scraper
python scripts/scrape_devpost.py

# Run MLH scraper
python scripts/scrape_mlh.py
```

## 🚨 Error Handling

The pipeline includes comprehensive error handling and logging:
- ❌ Failed API requests are logged and retried
- ✅ Data validation checks are performed at each stage
- 📧 Task failures trigger email notifications (when configured)

## 📊 Monitoring

Monitor the pipeline through:
- 📺 Airflow UI dashboard
- 📝 Logging system (configured to INFO level)
- 📈 AWS S3 bucket metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 🌟 Deploy to Astronomer

If you have an Astronomer account, you can deploy this project to Astronomer. For detailed deployment instructions, refer to [Astronomer's documentation](https://www.astronomer.io/docs/astro/deploy-code/).
