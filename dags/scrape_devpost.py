import requests
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

base_url = "https://devpost.com/api/hackathons"
total_pages = 5

logging.info("Starting the Devpost hackathon scraper.")
all_hackathons = fetch_hackathons(base_url, total_pages)
save_to_csv(all_hackathons, "data/devpost.csv")
logging.info("Devpost hackathon scraper finished.")
