# import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# def scrape_trulia_data(url):
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

#     try:
#         driver.get(url)

#         # Wait for the page to load
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "trulia-search-results-list")))

#         home_elements = driver.find_elements(By.XPATH, "//div[@class='trulia-search-result-card']")

#         homes_data = []
#         for home_element in home_elements:
#             home_data = {}
#             home_data['Type'] = home_element.find_element(By.CLASS_NAME, "trulia-search-result-property-type").text
#             home_data['Full Location'] = home_element.find_element(By.CLASS_NAME, "trulia-search-result-address").text
#             home_data['Price'] = home_element.find_element(By.CLASS_NAME, "trulia-search-result-price").text
#             home_data['URL'] = home_element.find_element(By.CLASS_NAME, "trulia-search-result-link").get_attribute('href')
#             # ... extract other details using appropriate XPaths or CSS selectors

#             homes_data.append(home_data)

#     finally:
#         driver.quit()

#     return homes_data

# # Get the initial URL from user input or define it directly
# initial_url = "https://www.trulia.com/GA/Atlanta/"

# # Set up pagination
# page = 1
# max_pages = 3  # Adjust the number of pages to scrape

# while page <= max_pages:
#     url = f"{initial_url}?page={page}"
#     homes_data = scrape_trulia_data(url)

#     # Save the data to a CSV file or process it further
#     # ...

#     page += 1

import time
import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def scrape_trulia_data(url):
    # Initialize undetected_chromedriver
    driver = uc.Chrome()

    homes_data = []

    try:
        driver.get(url)

        # Increase the wait time for page loading
        try:
            # Extend the timeout to 30 seconds
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "trulia-search-results-list")))
        except TimeoutException:
            print("Timeout: 'trulia-search-results-list' not found.")
            # Print the page source for debugging
            print(driver.page_source)
            return homes_data  # Return empty list if the element is not found

        # Find all home listing elements
        home_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'trulia-search-result-card')]")

        if not home_elements:
            print("No homes found on the page.")
        
        for home_element in home_elements:
            try:
                home_data = {}
                home_data['Type'] = home_element.find_element(By.XPATH, ".//div[contains(@class, 'property-type')]").text
                home_data['Full Location'] = home_element.find_element(By.XPATH, ".//div[contains(@class, 'address')]").text
                home_data['Price'] = home_element.find_element(By.XPATH, ".//div[contains(@class, 'price')]").text
                home_data['URL'] = home_element.find_element(By.XPATH, ".//a[contains(@class, 'search-result-link')]").get_attribute('href')

                homes_data.append(home_data)
            except Exception as e:
                print(f"Error extracting home data: {e}")

    finally:
        driver.quit()

    return homes_data

def save_to_csv(homes_data, filename):
    # Save data to CSV
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Type', 'Full Location', 'Price', 'URL'])
        
        # Write header if file is new
        if file.tell() == 0:
            writer.writeheader()
        
        for home in homes_data:
            writer.writerow(home)

# Get the initial URL from user input or define it directly
initial_url = "https://www.trulia.com/GA/Atlanta/"

# Set up pagination
page = 1
max_pages = 3  # Adjust the number of pages to scrape

while page <= max_pages:
    url = f"{initial_url}?page={page}"
    homes_data = scrape_trulia_data(url)
    
    if homes_data:
        save_to_csv(homes_data, 'trulia_data.csv')

    page += 1
    time.sleep(2)  # Small delay to avoid overwhelming the server

