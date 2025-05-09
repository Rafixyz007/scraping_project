import time
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from tqdm import tqdm
import logging
import os

# Configuration
DRIVER_PATH = "D:\\scraping\\selenium+bs4 infinte scroll\\geckodriver-v0.36.0-win64\\geckodriver.exe"
OUTPUT_FILE = "ycombinator_companies.csv"
BASE_URL = "https://www.ycombinator.com"
TARGET_URL = f"{BASE_URL}/companies?industry=Education"

'''
you can change this url to get any company information from this website
TARGET_URL = f"{BASE_URL}/companies?industry=Education"

'''
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    if not os.path.exists(DRIVER_PATH):
        raise FileNotFoundError(f"Geckodriver not found at: {DRIVER_PATH}")
    options = Options()
    # options.add_argument("--headless")  # Uncomment to run headless
    return webdriver.Firefox(service=Service(DRIVER_PATH), options=options)

def scroll_and_get_links(driver):
    driver.get(TARGET_URL)
    last_height = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return [BASE_URL + a["href"] for a in soup.select("a._company_i9oky_355")]

def clean(text):
    return text.strip() if text else None

def clean_url(url):
    return url.split('?')[0].split('#')[0].rstrip('/') if url else None

def extract_details(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        data = {
            'name': clean(soup.find("h1") and soup.find("h1").text),
            'slogan': clean(soup.select_one("div.text-xl") and soup.select_one("div.text-xl").text),
            'website': clean_url(soup.select_one("a.mb-2") and soup.select_one("a.mb-2")["href"]),
            'status': clean(soup.select_one("span.flex.items-center") and soup.select_one("span.flex.items-center").text),
            'founded': None, 'location': None, 'team_size': None, 'batch': None,
            'twitter': None, 'facebook': None, 'crunchbase': None
        }

        for row in soup.select("div.space-y-2.pt-4 div.flex.flex-row.justify-between"):
            spans = row.find_all("span")
            if len(spans) >= 2:
                label = spans[0].text.lower()
                value = spans[1].text.strip()
                if "founded" in label: data['founded'] = value
                elif "location" in label: data['location'] = value
                elif "team size" in label: data['team_size'] = value
                elif "batch" in label: data['batch'] = value

        for link in soup.select("div.flex.flex-wrap.items-center.gap-3.pt-2 a[href]"):
            href = clean_url(link['href'])
            if "twitter.com" in href or "x.com" in href:
                data['twitter'] = href
            elif "facebook.com" in href:
                data['facebook'] = href
            elif "crunchbase.com" in href:
                data['crunchbase'] = href

        return data
    except Exception as e:
        logging.error(f"Failed to extract from {url}: {e}")
        return None

def main():
    logging.info("Starting scraper...")
    try:
        driver = setup_driver()
        links = scroll_and_get_links(driver)
        driver.quit()
        logging.info(f"Found {len(links)} company pages")

        results = []
        for link in tqdm(links, desc="Scraping"):
            data = extract_details(link)
            if data:
                results.append(data)
            time.sleep(random.uniform(0.5, 1.5))

        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
        logging.info(f"Saved {len(results)} records to {OUTPUT_FILE}")
    except Exception as e:
        logging.error(f"Scraping failed: {e}")

if __name__ == "__main__":
    main()
#
#

