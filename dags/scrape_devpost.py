import requests
import csv
import logging
import boto3
from io import StringIO
import os

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
total_pages = 3
bucket_name = "my-hackathon-data-bucket"  # Replace with your bucket name
file_name = "devpost.csv"

logging.info("Starting the Devpost hackathon scraper.")
all_hackathons = fetch_hackathons(base_url, total_pages)
save_to_s3(all_hackathons, bucket_name, file_name)
logging.info("Devpost hackathon scraper finished.")
