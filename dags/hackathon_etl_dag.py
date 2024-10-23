from airflow.decorators import dag, task
from datetime import datetime, timedelta
import boto3
import pandas as pd
from io import StringIO
import logging
import os
import requests
from bs4 import BeautifulSoup
import csv
from airflow.hooks.base import BaseHook

# Set up logging
logging.basicConfig(level=logging.INFO)

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
        conn = BaseHook.get_connection('aws_s3')
        session = boto3.Session(
        aws_access_key_id=conn.login,
        aws_secret_access_key=conn.password,
        region_name='ap-south-1'
        )

        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        def fetch_hackathons(base_url, total_pages):
            all_hackathons = []
            headers = {
                'User-Agent': 'Mozilla/5.0'
            }

            for page in range(1, total_pages + 1):
                url = f"{base_url}?page={page}"
                logging.info(f"Fetching data from URL: {url}")
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    logging.info(f"Successfully fetched data from page {page}")
                    data = response.json()
                    hackathons = data.get('hackathons', [])
                    if not hackathons:
                        logging.warning(f"No hackathons found on page {page}")

                    for hackathon in hackathons:
                        title = hackathon.get('title')
                        location = hackathon.get('location', 'Online')
                        submission_period_dates = hackathon.get('submission_period_dates', 'N/A')
                        hackathon_url = hackathon.get('url')

                        all_hackathons.append({
                            'Title': title,
                            'Location': location,
                            'Dates': submission_period_dates,
                            'URL': hackathon_url
                        })
                else:
                    logging.error(f"Failed to fetch data from page {page}. Status code: {response.status_code}")

            return all_hackathons

        def save_to_s3(hackathons, bucket_name, file_name):
            if hackathons:
                fieldnames = ['Title', 'Location', 'Dates', 'URL']
                csv_buffer = StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
                writer.writeheader()
                for hackathon in hackathons:
                    writer.writerow(hackathon)
                
                s3_resource = boto3.resource('s3')
                s3_resource.Object(bucket_name, file_name).put(Body=csv_buffer.getvalue())
                logging.info(f"Successfully saved data to S3 bucket: {bucket_name}/{file_name}")
            else:
                logging.warning("No hackathons to save.")

        # Main execution
        base_url = "https://devpost.com/api/hackathons"
        total_pages = 100
        bucket_name = "my-hackathon-data-bucket"  # Replace with your bucket name
        file_name = "devpost.csv"

        logging.info("Starting the Devpost hackathon scraper.")
        all_hackathons = fetch_hackathons(base_url, total_pages)
        save_to_s3(all_hackathons, bucket_name, file_name)
        logging.info("Devpost hackathon scraper finished.")


    @task()
    def scrape_mlh():
        conn = BaseHook.get_connection('aws_s3')
        session = boto3.Session(
        aws_access_key_id=conn.login,
        aws_secret_access_key=conn.password,
        region_name='ap-south-1'
        )
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        def fetch_hackathons(base_url):
            all_hackathons = []
            headers = {
                'User-Agent': 'Mozilla/5.0'
            }

            logging.info(f"Fetching data from URL: {base_url}")
            response = requests.get(base_url, headers=headers)

            if response.status_code == 200:
                logging.info("Successfully fetched data")
                soup = BeautifulSoup(response.text, 'html.parser')
                hackathons = soup.find_all('div', class_='event')

                for hackathon in hackathons:
                    title_tag = hackathon.find('h3', class_='event-name')
                    title = title_tag.get_text(strip=True) if title_tag else 'N/A'
                    date_tag = hackathon.find('p', class_='event-date')
                    dates = date_tag.get_text(strip=True) if date_tag else 'N/A'
                    location_tag = hackathon.find('div', class_='event-location')
                    location = location_tag.get_text(strip=True) if location_tag else 'Online'
                    url_tag = hackathon.find('a', class_='event-link')
                    hackathon_url = url_tag['href'] if url_tag else 'N/A'

                    all_hackathons.append({
                        'Title': title,
                        'Location': location,
                        'Dates': dates,
                        'URL': hackathon_url
                    })
            else:
                logging.error(f"Failed to fetch data. Status code: {response.status_code}")

            return all_hackathons

        def save_to_s3(hackathons, bucket_name, file_name):
            if hackathons:
                fieldnames = ['Title', 'Location', 'Dates', 'URL']
                csv_buffer = StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
                writer.writeheader()
                for hackathon in hackathons:
                    writer.writerow(hackathon)

                s3_resource = boto3.resource('s3')
                s3_resource.Object(bucket_name, file_name).put(Body=csv_buffer.getvalue())
                logging.info(f"Successfully saved data to S3 bucket: {bucket_name}/{file_name}")
            else:
                logging.warning("No hackathons to save.")

        # Main execution
        base_url = "https://mlh.io/seasons/2025/events"
        bucket_name = "my-hackathon-data-bucket"  # Replace with your bucket name
        file_name = "mlh.csv"

        logging.info("Starting the MLH hackathon scraper.")
        all_hackathons = fetch_hackathons(base_url)
        save_to_s3(all_hackathons, bucket_name, file_name)
        logging.info("MLH hackathon scraper finished.")

    @task()
    def combine_and_clean():
        conn = BaseHook.get_connection('aws_s3')
        session = boto3.Session(
        aws_access_key_id=conn.login,
        aws_secret_access_key=conn.password,
        region_name='ap-south-1'
        )
        
        bucket_name = "my-hackathon-data-bucket"  # Replace with your bucket name
        devpost_key = 'devpost.csv'
        mlh_key = 'mlh.csv'
        combined_key = 'combined.csv'

        s3_client = boto3.client('s3')

        # Fetch Devpost CSV from S3
        devpost_obj = s3_client.get_object(Bucket=bucket_name, Key=devpost_key)
        devpost_csv = devpost_obj['Body'].read().decode('utf-8')
        df_devpost = pd.read_csv(StringIO(devpost_csv))

        # Fetch MLH CSV from S3
        mlh_obj = s3_client.get_object(Bucket=bucket_name, Key=mlh_key)
        mlh_csv = mlh_obj['Body'].read().decode('utf-8')
        df_mlh = pd.read_csv(StringIO(mlh_csv))

        # Perform your combination and cleaning
        df_combined = pd.concat([df_devpost, df_mlh])
        df_cleaned = df_combined.drop_duplicates().reset_index(drop=True)

        # Save the cleaned CSV file back to S3
        csv_buffer = StringIO()
        df_cleaned.to_csv(csv_buffer, index=False)
        s3_client.put_object(Bucket=bucket_name, Key=combined_key, Body=csv_buffer.getvalue())
        logging.info(f"Successfully saved combined CSV to S3: {bucket_name}/{combined_key}")

    # Define task dependencies
    scrape_devpost_task = scrape_devpost()
    scrape_mlh_task = scrape_mlh()
    combine_clean_task = combine_and_clean()

    # Both scraping tasks should be completed before combining and cleaning
    [scrape_devpost_task, scrape_mlh_task] >> combine_clean_task

# Instantiate the DAG
hackathon_etl_pipeline()