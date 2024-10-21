import requests
from bs4 import BeautifulSoup
import csv
import logging

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
            logging.error(f"Failed to fetch data from page {page}. Status code: {response.status_code}")

    return all_hackathons

def save_to_csv(hackathons, filename):
    if hackathons:
        fieldnames = ['Title', 'Location', 'Dates', 'URL']
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for hackathon in hackathons:
                    writer.writerow(hackathon)
            logging.info(f"Successfully saved data to {filename}")
        except Exception as e:
            logging.error(f"Failed to save data to {filename}. Error: {e}")
    else:
        logging.warning("No hackathons to save.")

base_url = "https://mlh.io/seasons/2025/events"
total_pages = 1

logging.info("Starting the MLH hackathon scraper.")
all_hackathons = fetch_hackathons(base_url, total_pages)
save_to_csv(all_hackathons, "/usr/local/airflow/data/data/mlh.csv")
logging.info("MLH hackathon scraper finished.")
