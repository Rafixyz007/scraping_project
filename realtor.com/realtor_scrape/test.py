import requests
import json
import pandas as pd

url = "https://www.realtor.com/frontdoor/graphql"

def fetch_page_data(offset=0, limit=42):
    # Adjusted payload based on corrected type
    payload = {
        "query": """
            query getFocusedSearchDataQuery($params: FocusedSearchParams!) {
                rentals_focused_search_data(params: $params) {
                    name
                    location_scores {
                        point_scores {
                            label
                            value
                            text
                            icon_url
                            groups
                            __typename
                        }
                        vendor {
                            disclaimer
                            url {
                                href
                                text
                                message
                                __typename
                            }
                            logo
                            __typename
                        }
                        group_categories
                        overall_average_score
                        group_scores {
                            label
                            value
                            icon_url
                            __typename
                        }
                        __typename
                    }
                    count
                    slug_id
                    centroid {
                        lat
                        lon
                        __typename
                    }
                    __typename
                }
            }
        """,
        "variables": {
            "params": {
                "search_location": {
                    "location": "Macon, GA"
                },
                "limit": limit,
                "offset": offset
            }
        }
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'cookie': 'your_cookie_here',  # Replace with actual cookie if needed
        'origin': 'https://www.realtor.com',
        'priority': 'u=1, i',
        'rdc-client-name': 'RDC_WEB_SRP_FS_PAGE',
        'rdc-client-version': '3.x.x',
        'referer': 'https://www.realtor.com/realestateandhomes-search/Macon_GA',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin'
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print("Fetching data for offset", offset)

        # Print the response status and content for debugging
        print("Response Status Code:", response.status_code)
        print("Response Content:", response.text)

        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx

        data = response.json()
        print("Raw response:", json.dumps(data, indent=4))  # Print raw response for debugging

        if data and 'data' in data and 'rentals_focused_search_data' in data['data']:
            return data['data']['rentals_focused_search_data']
        else:
            print("No data found or invalid response format.")
            return []

    except requests.exceptions.RequestException as e:
        print(f"HTTP error occurred: {e}")
        return []
    except json.JSONDecodeError:
        print("Error decoding the JSON response")
        return []

def scrape_all_pages(limit=42):
    all_properties = []
    offset = 0

    while True:
        print(f"Fetching data for offset {offset}...")
        properties = fetch_page_data(offset, limit)
        
        if not properties:
            break

        all_properties.extend(properties)
        offset += limit

        # For testing purposes, stop after fetching a fixed number of items
        if len(all_properties) >= 42:
            break

    return all_properties

def main():
    all_data = scrape_all_pages()
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_excel('all_properties_details.xlsx', index=False)
        print("Data saved to 'all_properties_details.xlsx'")
    else:
        print("No data to save.")

if __name__ == "__main__":
    main()
