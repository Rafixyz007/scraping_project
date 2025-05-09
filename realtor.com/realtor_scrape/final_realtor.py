import requests
import json
import pandas as pd

url = "https://www.realtor.com/frontdoor/graphql"

# Function to fetch data for a single page
def fetch_page_data(offset):
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
                    search_promotion {
                        names
                        slots
                        promoted_properties {
                            id
                            from_other_page
                            __typename
                        }
                        __typename
                    }
                    mortgage_params {
                        interest_rate
                        __typename
                    }
                    properties: results {
                        property_id
                        list_price
                        search_promotions {
                            name
                            asset_id
                            __typename
                        }
                        primary_photo(https: true) {
                            href
                            __typename
                        }
                        rent_to_own {
                            right_to_purchase
                            rent
                            __typename
                        }
                        listing_id
                        matterport
                        virtual_tours {
                            href
                            type
                            __typename
                        }
                        status
                        products {
                            products
                            brand_name
                            __typename
                        }
                        source {
                            id
                            type
                            spec_id
                            plan_id
                            agents {
                                office_name
                                __typename
                            }
                            __typename
                        }
                        lead_attributes {
                            show_contact_an_agent
                            opcity_lead_attributes {
                                cashback_enabled
                                flip_the_market_enabled
                                __typename
                            }
                            lead_type
                            ready_connect_mortgage {
                                show_contact_a_lender
                                show_veterans_united
                                __typename
                            }
                            __typename
                        }
                        community {
                            description {
                                name
                                __typename
                            }
                            property_id
                            permalink
                            advertisers {
                                office {
                                    hours
                                    phones {
                                        type
                                        number
                                        primary
                                        trackable
                                        __typename
                                    }
                                    __typename
                                }
                                __typename
                            }
                            promotions {
                                description
                                href
                                headline
                                __typename
                            }
                            __typename
                        }
                        permalink
                        price_reduced_amount
                        description {
                            name
                            beds
                            baths_consolidated
                            sqft
                            lot_sqft
                            baths_max
                            baths_min
                            beds_min
                            beds_max
                            sqft_min
                            sqft_max
                            type
                            sub_type
                            sold_price
                            sold_date
                            __typename
                        }
                        location {
                            street_view_url
                            address {
                                line
                                postal_code
                                state
                                state_code
                                city
                                coordinate {
                                    lat
                                    lon
                                    __typename
                                }
                                __typename
                            }
                            county {
                                name
                                fips_code
                                __typename
                            }
                            __typename
                        }
                        open_houses {
                            start_date
                            end_date
                            __typename
                        }
                        branding {
                            type
                            name
                            photo
                            __typename
                        }
                        flags {
                            is_coming_soon
                            is_new_listing(days: 14)
                            is_price_reduced(days: 30)
                            is_foreclosure
                            is_new_construction
                            is_pending
                            is_contingent
                            __typename
                        }
                        list_date
                        photos(limit: 2, https: true) {
                            href
                            __typename
                        }
                        advertisers {
                            type
                            builder {
                                name
                                href
                                logo
                                __typename
                            }
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
                commute_polygon: get_commute_polygon(query: $query) {
                    areas {
                        id
                        breakpoints {
                            width
                            height
                            zoom
                            __typename
                        }
                        radius
                        center {
                            lat
                            lng
                            __typename
                        }
                        __typename
                    }
                    boundary
                    __typename
                }
            }
        """,
        "variables": {
            "query": {
                "primary": True,
                "status": ["for_sale", "ready_to_build"],
                "search_location": {"location": "Macon, GA"}
            },
            "client_data": {"device_data": {"device_type": "tablet"}},
            "limit": 42,
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
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        
        # Parse the JSON response
        data = response.json()
        
        # Check if there is any data
        if 'data' in data and 'home_search' in data['data'] and 'properties' in data['data']['home_search']:
            return data['data']['home_search']['properties']
        else:
            print("No data found for offset:", offset)
            return []

    except requests.exceptions.RequestException as e:
        print(f"HTTP error occurred: {e}")
        return []

# Function to scrape all pages
def scrape_all_pages():
    offset = 0
    limit = 42  # Number of results per page
    all_properties = []
    
    while True:
        print(f"Fetching data for offset {offset}...")
        properties = fetch_page_data(offset)
        
        if not properties:
            break
        
        all_properties.extend(properties)
        offset += limit  # Move to the next page
    
    return all_properties

# Main script
def main():
    all_data = scrape_all_pages()
    
    if all_data:
        # Convert to DataFrame and save to excel
        df = pd.json_normalize(all_data)
        df.to_excel('all_properties_details.xlsx', index=False)
        print("Data saved to all_properties_details.xlsx")
    else:
        print("No data found.")

if __name__ == "__main__":
    main()

