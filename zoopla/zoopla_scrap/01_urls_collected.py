from undetected_chromedriver import Chrome
import time

chrome = Chrome()

# url = 'https://www.zoopla.co.uk/for-sale/property/london/?q=London&results_sort=newest_listings&search_source=for-sale'

# chrome.get(url)

for page in range(1,6):
    url = f'https://www.zoopla.co.uk/for-sale/property/london/?q=London&results_sort=newest_listings&search_source=for-sale&pn={page}'
    chrome.get(url)
    time.sleep(3)

    urls = chrome.find_elements('xpath','//div[@class="_1lw0o5c0"]//a[@class="_1lw0o5c1"]')

    with open('url.txt','a') as file:
        for url_ in urls:
            url_link = url_.get_attribute('href')
            file.write(url_link + '\n')  # Write each URL to a new line
            print(url_link)


chrome.quit()
