import requests
from bs4 import BeautifulSoup
import csv
import logging
import boto3
from io import StringIO
import os

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