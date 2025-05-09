from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)

options = ChromeOptions()
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')

driver = Chrome(options=options)

df = pd.DataFrame(columns=['Price', 'Flat Type', 'Address', 'Additional Info', 'Key Features', 'Description', 'Local Info', 'Agent Name', 'Agent Address', 'Agent Mobile NO'])

# Function to dismiss cookie banner
def dismiss_cookie_banner(driver):
    try:
        cookie_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')))
        cookie_button.click()
        logging.info("Cookie consent dismissed.")
    except Exception as e:
        logging.warning(f"No cookie consent found or failed to dismiss: {e}")

# Function to extract text by XPath
def extract_text(driver, xpath, default='Not Available'):
    try:
        return driver.find_element(By.XPATH, xpath).text
    except Exception:
        return default

# Function to click the "View agent properties" link
def click_agent_properties(driver):
    try:
        link = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, 'View agent properties')))
        driver.execute_script("arguments[0].scrollIntoView(true);", link)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(link)).click()
        logging.info("Link clicked successfully.")
    except Exception as e:
        logging.warning(f"Error locating or clicking the link: {e}")

# Process each URL
with open('url.txt', 'r') as file:
    for url in file:
        url = url.strip()
        try:
            logging.info(f"\nProcessing URL: {url}")
            driver.get(url)

            # Wait for page to load
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//p[@class="_64if862 _194zg6t6"]')))
            dismiss_cookie_banner(driver)

            # Extract the required data
            price = extract_text(driver, '//p[@class="_64if862 _194zg6t6"]')
            flat_type = extract_text(driver, '//p[@class="_1olqsf98"]')
            address = extract_text(driver, '//address[@class="_1olqsf99"]')
            additional_info = extract_text(driver, '//ul[@class="_1olqsf9a"]')
            description = extract_text(driver, '//section[@aria-labelledby="about"]//p[@id="detailed-desc"]')
            agent_name = extract_text(driver, '//p[@class="_194zg6t7 _133vwz72"]')

            # Extract key features and local info i use join because this two has multiple data
            key_features = ', '.join([el.text for el in driver.find_elements(By.XPATH, '//section[@aria-labelledby="about"]//ul[@class="_15a8ens0"]/li/p/span[2]')])
            local_info = ', '.join([li.text for ul in driver.find_elements(By.XPATH, '//ul[@class="b1ub3l1"]') for li in ul.find_elements(By.TAG_NAME, 'li')])

            # Click on the "View agent properties" link to extract agent address and mobile number
            click_agent_properties(driver)
            agent_address = extract_text(driver, '//*[@id="main-content"]/div/div[1]/div[1]/div[1]/p[1]')
            agent_cell_no = extract_text(driver, '//*[@id="main-content"]/div/div[1]/div[1]/div[1]/p[2]/a[1]/span[2]', 'Not Available')

            # Append the data to the DataFrame
            df = pd.concat([df, pd.DataFrame([{
                'Price': price, 'Flat Type': flat_type, 'Address': address, 'Additional Info': additional_info,
                'Key Features': key_features, 'Description': description, 'Local Info': local_info,
                'Agent Name': agent_name, 'Agent Address': agent_address, 'Agent Mobile NO': agent_cell_no
            }])], ignore_index=True)

        except Exception as e:
            logging.error(f"Error processing {url}: {e}")

# Save the DataFrame to an Excel file
df.to_excel('zoopla_scraped_data.xlsx', index=False)

# Close the browser
driver.quit()

