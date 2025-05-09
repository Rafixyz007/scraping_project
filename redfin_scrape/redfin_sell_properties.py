import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Initialize Chrome options
options = uc.ChromeOptions()
# options.add_argument("--headless")  # Uncomment if you want to run headless
options.add_argument('--no-sandbox') 

''' --no-sandbox
Purpose: This option disables the Chrome sandboxing feature.
Why Use It:
Compatibility: Some environments, like certain Docker containers or CI/CD pipelines, may not support sandboxing properly. Disabling it can help avoid crashes or errors related to sandboxing.
Permission Issues: In some cases, especially in environments with restricted permissions, Chrome might fail to launch or execute scripts properly due to sandboxing restrictions.
'''

options.add_argument('--disable-dev-shm-usage')

''' --disable-dev-shm-usage
Purpose: This option tells Chrome to use the /tmp directory instead of the /dev/shm directory for shared memory.
Why Use It:
Limited Shared Memory: On systems with limited /dev/shm space (like some Docker containers), Chrome can run out of shared memory, causing it to crash. This option directs it to use a different directory, which typically has more available space.
Stability: It can help improve stability in environments where the shared memory is insufficient for Chrome’s needs.

'''

# Launch undetected ChromeDriver
driver = uc.Chrome(options=options)

# Base URL for Redfin listings
base_url = "https://www.redfin.com/city/29470/IL/Chicago/filter/viewport=43.86323:40.49395:-86.69066:-90.57982,no-outline/page-{}"

# Initialize an empty DataFrame to store property details
property_data = []

# Loop through the pages (adjust the range as needed)
for page in range(1, 10):  # For example, scraping the first 5 pages
    url = base_url.format(page)  # Format the URL with the current page number
    driver.get(url)

    # Wait for property listings to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="bp-Homecard__Content"]')))

    # Get all property listings on the current page
    property_elements = driver.find_elements(By.XPATH, '//div[@class="bp-Homecard__Content"]')

    # Extract details for each property
    for property_element in property_elements:
        try:
            address = property_element.find_element(By.XPATH, './/div[@class="bp-Homecard__Address flex align-center color-text-primary font-body-xsmall-compact"]').text
            price = property_element.find_element(By.XPATH, './/span[@class="bp-Homecard__Price--value"]').text
            beds = property_element.find_element(By.XPATH, './/span[@class="bp-Homecard__Stats--beds text-nowrap"]').text
            baths = property_element.find_element(By.XPATH, './/span[@class="bp-Homecard__Stats--baths text-nowrap"]').text
            size = property_element.find_element(By.XPATH, './/span[@class="bp-Homecard__Stats--sqft text-nowrap"]').text
            
            # Append property details to the list
            property_data.append({
                'Address': address,
                'Price': price,
                'Beds': beds,
                'Baths': baths,
                'Size': size
            })
        except Exception as e:
            print(f"Error extracting property data: {e}")

    # Optional: Sleep for a few seconds to avoid overwhelming the server
    time.sleep(2)

df = pd.DataFrame(property_data)

# Save the DataFrame to a CSV file
df.to_csv('redfin_properties.csv', index=False)  # This line saves the data to a CSV file

# Close the browser
driver.quit()

