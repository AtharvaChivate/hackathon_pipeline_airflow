from airflow.decorators import dag, task
from datetime import datetime, timedelta
import os
import pandas as pd

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@dag(default_args=default_args, schedule_interval='@daily', start_date=datetime(2023, 10, 1), catchup=False)
def hackathon_etl_pipeline():
    """
    Airflow DAG to scrape data from Devpost and MLH, store in CSV files,
    then combine and clean the data.
    """

    @task()
    def scrape_devpost():
        os.system('python /opt/airflow/dags/scripts/scrape_devpost.py')

    @task()
    def scrape_mlh():
        os.system('python /opt/airflow/dags/scripts/scrape_mlh.py')

    @task()
    def combine_and_clean():
        devpost_csv = 'data/devpost.csv'
        mlh_csv = 'data/mlh.csv'

        # Check if files exist and have content
        if not os.path.exists(devpost_csv) or os.path.getsize(devpost_csv) == 0:
            raise Exception(f"File {devpost_csv} is missing or empty.")
        
        if not os.path.exists(mlh_csv) or os.path.getsize(mlh_csv) == 0:
            raise Exception(f"File {mlh_csv} is missing or empty.")
        
        # Proceed with reading
        df_devpost = pd.read_csv(devpost_csv)
        df_mlh = pd.read_csv(mlh_csv)

        # Perform your combination and cleaning
        df_combined = pd.concat([df_devpost, df_mlh])
        df_cleaned = df_combined.drop_duplicates().reset_index(drop=True)
        
        # Save the cleaned CSV file
        df_cleaned.to_csv('data/combined_cleaned.csv', index=False)


    # Define task dependencies
    scrape_devpost_task = scrape_devpost()
    scrape_mlh_task = scrape_mlh()
    combine_clean_task = combine_and_clean()

    # Both scraping tasks should be completed before combining and cleaning
    [scrape_devpost_task, scrape_mlh_task] >> combine_clean_task

# Instantiate the DAG
hackathon_etl_pipeline()
