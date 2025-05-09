import tkinter as tk
from tkinter import ttk
import requests
import json
import pandas as pd

def fetch_data():
    location = location_var.get()
    limit = int(limit_var.get())
    offset = int(offset_var.get())
    
    url = "https://www.realtor.com/frontdoor/graphql"
    
    payload = {
        "query": """
            query ConsumerSearchQuery(
                $query: HomeSearchCriteria!,
                $limit: Int,
                $offset: Int,
                $search_promotion: SearchPromotionInput,
                $sort: [SearchAPISort],
                $sort_type: SearchSortType,
                $client_data: JSON,
                $bucket: SearchAPIBucket,
                $mortgage_params: MortgageParamsInput
            ) {
                home_search(
                    query: $query
                    sort: $sort
                    limit: $limit
                    offset: $offset
                    sort_type: $sort_type
                    client_data: $client_data
                    bucket: $bucket
                    search_promotion: $search_promotion
                    mortgage_params: $mortgage_params
                ) {
                    count
                    total
                    properties: results {
                        property_id
                        list_price
                        description {
                            name
                            beds
                            baths_consolidated
                            sqft
                            __typename
                        }
                        location {
                            address {
                                city
                                __typename
                            }
                        }
                        __typename
                    }
                }
            }
        """,
        "variables": {
            "query": {
                "primary": True,
                "status": ["for_sale", "ready_to_build"],
                "search_location": {"location": location}
            },
            "client_data": {"device_data": {"device_type": "tablet"}},
            "limit": limit,
            "offset": offset,
            "sort_type": "relevant",
            "search_promotion": {
                "names": ["CITY"],
                "slots": [5, 6, 7, 8],
                "promoted_properties": [[], []]
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
        response.raise_for_status()  # Raise an error for HTTP errors
        
        data = response.json()
        
        # Check if 'data' is valid
        if not data or 'data' not in data:
            status_label.config(text="No data found or invalid response format.")
            return
        
        # Extract the properties
        properties = data.get('data', {}).get('home_search', {}).get('properties', [])
        df = pd.json_normalize(properties)
        
        # Save to CSV
        df.to_csv('properties.csv', index=False)
        
        # Update status
        status_label.config(text="Data fetched and saved to properties.csv.")
    
    except requests.exceptions.RequestException as e:
        status_label.config(text=f"Error fetching data: {e}")
    except json.JSONDecodeError as e:
        status_label.config(text=f"Error decoding JSON: {e}")

# Initialize Tkinter
root = tk.Tk()
root.title("Realtor Data Fetcher")

# Location dropdown
locations = ["Macon, GA", "Atlanta, GA", "Savannah, GA"]  # Add more locations as needed
location_var = tk.StringVar(value=locations[0])
location_label = tk.Label(root, text="Select Location:")
location_label.pack(pady=5)
location_dropdown = ttk.Combobox(root, textvariable=location_var, values=locations)
location_dropdown.pack(pady=5)

# Limit dropdown
limits = [10, 20, 30, 40, 50]
limit_var = tk.StringVar(value=limits[0])
limit_label = tk.Label(root, text="Select Limit:")
limit_label.pack(pady=5)
limit_dropdown = ttk.Combobox(root, textvariable=limit_var, values=limits)
limit_dropdown.pack(pady=5)

# Offset dropdown
offsets = [0, 1, 2, 3, 4, 5]
offset_var = tk.StringVar(value=offsets[0])
offset_label = tk.Label(root, text="Select Offset:")
offset_label.pack(pady=5)
offset_dropdown = ttk.Combobox(root, textvariable=offset_var, values=offsets)
offset_dropdown.pack(pady=5)

# Fetch button
fetch_button = tk.Button(root, text="Fetch Data", command=fetch_data)
fetch_button.pack(pady=10)

# Status label
status_label = tk.Label(root, text="")
status_label.pack(pady=5)

# Run Tkinter main loop
root.mainloop()

