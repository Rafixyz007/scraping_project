import requests
import json
import time
import csv


def get_all_trulia_data(initial_payload, csrf_token):
    url = "https://www.trulia.com/graphql?operation_name=WEB_searchHomesBySearchDetailsQuery&transactionId=92494831-9c65-4f68-91c6-07a106f222b0"
    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://www.trulia.com',
        'referer': 'https://www.trulia.com/GA/Atlanta/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'x-csrf-token': csrf_token,  # Directly use the CSRF token here
    }

    all_homes = []
    page = 1
    total_homes = None

    while True:
        print(f"Fetching page {page}...")

        # Update the page number in the payload
        payload = json.loads(initial_payload)
        payload['variables']['searchDetails']['filters']['page'] = page

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"Request failed with status code: {response.status_code}")
            break

        data = response.json()

        if 'errors' in data:
            print(f"API returned errors: {data['errors']}")
            break

        try:
            homes = data['data']['searchHomesByDetails']['homes']
            if total_homes is None:
                total_homes = data['data']['searchHomesByDetails']['totalHomes']
                print(f"Total homes: {total_homes}")

            all_homes.extend(homes)
            print(f"Fetched {len(homes)} homes from page {page}")

            if len(all_homes) >= total_homes:
                break

            page += 1
            time.sleep(2)  # Add a delay to avoid rate limiting

        except KeyError as e:
            print(f"Error fetching data: {e}")
            break

    return all_homes


def parse_home_data(home):
    parsed_data = {
        'Type': home.get('__typename', 'No Type Available'),
        'Full Location': home['location'].get('fullLocation', 'No Address Available'),
        'Price': home['price'].get('formattedPrice', 'No Price Available'),
        'URL': f"https://www.trulia.com{home.get('url', 'No URL Available')}",
        'Floor Space': home['floorSpace'].get('formattedDimension', 'No Floor Space Info Available') if home.get(
            'floorSpace') else 'No Floor Space Info Available',
        'Bedrooms': home['bedrooms'].get('formattedValue', 'No Bedrooms Info Available') if home.get(
            'bedrooms') else 'No Bedrooms Info Available',
        'Bathrooms': home['bathrooms'].get('formattedValue', 'No Bathrooms Info Available') if home.get(
            'bathrooms') else 'No Bathrooms Info Available',
        'Lot Size': home['lotSize'].get('formattedDimension', 'No Lot Size Info Available') if home.get(
            'lotSize') else 'No Lot Size Info Available',
    }

    # Add more fields as needed
    if 'currentStatus' in home:
        parsed_data['Status'] = {
            'Is For Sale': home['currentStatus'].get('isActiveForSale', False),
            'Is For Rent': home['currentStatus'].get('isActiveForRent', False),
            'Is Off Market': home['currentStatus'].get('isOffMarket', False),
            'Is Foreclosure': home['currentStatus'].get('isForeclosure', False),
        }

    if 'tags' in home:
        parsed_data['Tags'] = [tag['formattedName'] for tag in home['tags']]
    else:
        parsed_data['Tags'] = []

    return parsed_data


def save_to_csv(homes, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['Type', 'Full Location', 'Price', 'URL', 'Floor Space', 'Bedrooms', 'Bathrooms', 'Lot Size',
                      'Status', 'Tags']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for home in homes:
            parsed_home = parse_home_data(home)
            # Flatten the status dictionary for CSV
            status = ', '.join([f"{key}: {value}" for key, value in
                                parsed_home['Status'].items()]) if 'Status' in parsed_home else 'No Status Available'
            tags = ', '.join(parsed_home['Tags']) if 'Tags' in parsed_home else 'No Tags Available'
            # Write the data row
            writer.writerow({
                'Type': parsed_home['Type'],
                'Full Location': parsed_home['Full Location'],
                'Price': parsed_home['Price'],
                'URL': parsed_home['URL'],
                'Floor Space': parsed_home['Floor Space'],
                'Bedrooms': parsed_home['Bedrooms'],
                'Bathrooms': parsed_home['Bathrooms'],
                'Lot Size': parsed_home['Lot Size'],
                'Status': status,
                'Tags': tags,
            })


# Your initial payload string goes here
initial_payload = ("{\"query\":\"query WEB_searchHomesBySearchDetailsQuery($searchDetails: SEARCHDETAILS_Input!, "
           "$heroImageFallbacks: [MEDIA_HeroImageFallbackTypes!], $isBot: Boolean!, $defaultSortType: "
           "SEARCHDETAILS_SortType = null, $defaultSortDirection: SEARCHDETAILS_SortDirection = null, $includeNearBy: "
           "Boolean = true, $isNearbyCitiesEnabled: Boolean = false, $isInSeoLongTermRentalTitleTest: Boolean = "
           "false, $inFooterTest: Boolean = false, $inCrossSellTest: Boolean = false, $crossSellVariation: "
           "SEARCH_CrossSellModuleVariation, $includeReviewHighlights: Boolean = false) {\\n  searchHomesByDetails("
           "\\n    searchDetails: $searchDetails\\n    defaultSortType: $defaultSortType\\n    defaultSortDirection: "
           "$defaultSortDirection\\n    includeNearBy: $includeNearBy\\n  ) {\\n    "
           "...SearchResultsContentFragment\\n    __typename\\n  }\\n}\\n\\nfragment SearchResultsContentFragment on "
           "SEARCH_Result {\\n  currentUrl\\n  canonicalUrl\\n  secondaryNavigation(inFooterTest: $inFooterTest) {\\n "
           "   inFooterTest\\n    __typename\\n  }\\n  adTargetings @skip(if: $isBot)\\n  "
           "...SearchResultHeaderLocationFragment\\n  ...SearchResultsMarketDetailsFragment @include(if: $isBot)\\n  "
           "...SearchResultsMarketDetailsFragment @include(if: $inFooterTest)\\n  "
           "...SearchResultsHomesListFragment\\n  ...SearchResultsPaginationFragment\\n  "
           "...SearchResultsBreadcrumbsFragment\\n  ...SearchResultsPopularLocationsFragment\\n  "
           "...SearchResultsMapFragment\\n  ...SearchResultsFooterCardFragment\\n  ...SearchResultsFiltersFragment\\n "
           " ...SearchResultsProviderAttributionFragment\\n  ...SearchResultsRentalJsonLdSchemaFragment\\n  homes {"
           "\\n    ...SearchResultsRentalResultJsonLdSchemaFragment\\n    ...HiddenHomeSrpFragment\\n    "
           "__typename\\n  }\\n  details {\\n    ...SearchDetailsFragment\\n    canonicalUrl\\n    __typename\\n  "
           "}\\n  names(isInSeoLongTermRentalTitleTest: $isInSeoLongTermRentalTitleTest) {\\n    title\\n    "
           "locationName\\n    description\\n    __typename\\n  }\\n  tracking {\\n    key\\n    value\\n    "
           "__typename\\n  }\\n  pageDisplayFlags {\\n    isAdvertisingRestricted\\n    __typename\\n  }\\n  "
           "nearByHomes {\\n    ...HomeDetailsCardFragment\\n    ...HomeDetailsCardPhotosFragment\\n    "
           "...SingleFamilyResidenceJsonLdFragment\\n    ...OpenHouseJsonLdFragment\\n    "
           "...HomeDetailsCallToActionFragment\\n    ...HiddenHomeSrpFragment\\n    __typename\\n  }\\n  openHomes {"
           "\\n    inPerson {\\n      ...OpenHouseJsonLdFragment\\n      __typename\\n    }\\n    __typename\\n  }\\n "
           " dynamicFilters {\\n    homeTypes {\\n      name\\n      searchUrl\\n      __typename\\n    }\\n    "
           "listingTypes {\\n      name\\n      searchUrl\\n      __typename\\n    }\\n    __typename\\n  }\\n  "
           "location {\\n    encodedPolygon\\n    __typename\\n  }\\n  isSrpIndexable\\n  preferences {\\n    isSaved "
           "@skip(if: $isBot)\\n    __typename\\n  }\\n  ...CrossSellModuleFragment @include(if: $inCrossSellTest)\\n "
           " ...ExploreCollectionsFragmentBot @include(if: $isBot)\\n  __typename\\n}\\n\\nfragment "
           "SearchResultHeaderLocationFragment on SEARCH_Result {\\n  location {\\n    ... on "
           "SEARCH_ResultLocationState {\\n      state\\n      __typename\\n    }\\n    ... on "
           "SEARCH_ResultLocationBoundingBox {\\n      city\\n      state\\n      __typename\\n    }\\n    ... on "
           "SEARCH_ResultLocationCity {\\n      city\\n      state\\n      __typename\\n    }\\n    ... on "
           "SEARCH_ResultLocationCounty {\\n      county\\n      state\\n      __typename\\n    }\\n    ... on "
           "SEARCH_ResultLocationNeighborhood {\\n      city\\n      state\\n      neighborhood\\n      __typename\\n "
           "   }\\n    ... on SEARCH_ResultLocationPostalCode {\\n      city\\n      state\\n      postalCode\\n      "
           "__typename\\n    }\\n    ... on SEARCH_ResultLocationSchool {\\n      name\\n      __typename\\n    }\\n  "
           "  ... on SEARCH_ResultLocationSchoolDistrict {\\n      city\\n      state\\n      schoolDistrictIds\\n    "
           "  __typename\\n    }\\n    ... on SEARCH_ResultLocationCommute {\\n      exactCoordinates {\\n        "
           "latitude\\n        longitude\\n        __typename\\n      }\\n      __typename\\n    }\\n    "
           "__typename\\n  }\\n  recentSearches {\\n    title\\n    type\\n    url\\n    locationDetails {\\n      "
           "cities {\\n        city\\n        state\\n        __typename\\n      }\\n      counties\\n      "
           "neighborhoods\\n      zips\\n      schoolDistricts\\n      school {\\n        id\\n        name\\n        "
           "__typename\\n      }\\n      commute {\\n        type\\n        __typename\\n      }\\n      "
           "__typename\\n    }\\n    formattedFilterLists\\n    __typename\\n  }\\n  pageDisplayFlags {\\n    "
           "shouldDisplayZINCAttribution\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment "
           "SearchResultsHomesListFragment on SEARCH_Result {\\n  homeCounts {\\n    agentListingsCount {\\n      "
           "value\\n      __typename\\n    }\\n    otherListingsCount {\\n      value\\n      __typename\\n    }\\n   "
           " resultCount {\\n      formattedValue\\n      __typename\\n    }\\n    __typename\\n  }\\n  homes {\\n    "
           "...HomeDetailsCardFragment\\n    ...HomeDetailsCardPhotosFragment\\n    "
           "...SingleFamilyResidenceJsonLdFragment\\n    ...OpenHouseJsonLdFragment\\n    "
           "...HomeDetailsCallToActionFragment\\n    __typename\\n  }\\n  ...FailedSearchFragment\\n  names("
           "isInSeoLongTermRentalTitleTest: $isInSeoLongTermRentalTitleTest) {\\n    headerTag\\n    subHeaderTag\\n  "
           "  resultsIncludeDescription\\n    searchResultsMapTag\\n    nearByHeaderTag\\n    nearBySubHeaderTag\\n   "
           " formattedFilterLists\\n    __typename\\n  }\\n  totalHomes\\n  details {\\n    "
           "...SearchResultsSortFragment\\n    __typename\\n  }\\n  emptyState {\\n    noHomesFoundText\\n    "
           "noHomesFoundCTAText\\n    reason\\n    __typename\\n  }\\n  moreHomesInformation {\\n    title\\n    "
           "body\\n    ctaTitle\\n    __typename\\n  }\\n  dynamicFilters {\\n    neighborhoods {\\n      value\\n    "
           "  displayText\\n      isActive\\n      count\\n      __typename\\n    }\\n    neighborhoodRegions {\\n    "
           "  value\\n      displayText\\n      isActive\\n      count\\n      __typename\\n    }\\n    __typename\\n "
           " }\\n  isSaveSearchCardVisible\\n  availableExploreCollections\\n  __typename\\n}\\n\\nfragment "
           "HomeDetailsCardFragment on HOME_Details {\\n  __typename\\n  location {\\n    city\\n    stateCode\\n    "
           "zipCode\\n    streetAddress\\n    fullLocation: formattedLocation(formatType: STREET_CITY_STATE_ZIP)\\n   "
           " partialLocation: formattedLocation(formatType: STREET_ONLY)\\n    __typename\\n  }\\n  price {\\n    "
           "formattedPrice\\n    ... on HOME_ValuationPrice {\\n      typeDescription(abbreviate: true)\\n      "
           "__typename\\n    }\\n    __typename\\n  }\\n  url\\n  homeUrl\\n  tags(include: MINIMAL) {\\n    level\\n "
           "   formattedName\\n    icon {\\n      vectorImage {\\n        svg\\n        __typename\\n      }\\n      "
           "__typename\\n    }\\n    __typename\\n  }\\n  fullTags: tags {\\n    level\\n    formattedName\\n    icon "
           "{\\n      vectorImage {\\n        svg\\n        __typename\\n      }\\n      __typename\\n    }\\n    "
           "__typename\\n  }\\n  floorSpace {\\n    formattedDimension\\n    __typename\\n  }\\n  lotSize {\\n    ... "
           "on HOME_SingleDimension {\\n      formattedDimension(minDecimalDigits: 2, maxDecimalDigits: 2)\\n      "
           "__typename\\n    }\\n    __typename\\n  }\\n  bedrooms {\\n    formattedValue(formatType: "
           "TWO_LETTER_ABBREVIATION)\\n    __typename\\n  }\\n  bathrooms {\\n    formattedValue(formatType: "
           "TWO_LETTER_ABBREVIATION)\\n    __typename\\n  }\\n  isSaveable\\n  preferences {\\n    isSaved\\n    "
           "__typename\\n  }\\n  metadata {\\n    compositeId\\n    legacyIdForSave\\n    unifiedListingType\\n    "
           "typedHomeId\\n    __typename\\n  }\\n  typedHomeId\\n  tracking {\\n    key\\n    value\\n    "
           "__typename\\n  }\\n  displayFlags {\\n    showMLSLogoOnListingCard\\n    "
           "addAttributionProminenceOnListCard\\n    __typename\\n  }\\n  ... on HOME_RoomForRent {\\n    "
           "numberOfRoommates\\n    availableDate: formattedAvailableDate(dateFormat: \\\"MMM D\\\")\\n    "
           "providerListingId\\n    __typename\\n  }\\n  ... on HOME_RentalCommunity {\\n    activeListing {\\n      "
           "provider {\\n        summary(formatType: SHORT)\\n        listingSource {\\n          logoUrl\\n          "
           "__typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    location {\\n      "
           "communityLocation: formattedLocation(formatType: STREET_COMMUNITY_NAME)\\n      __typename\\n    }\\n    "
           "providerListingId\\n    __typename\\n  }\\n  ... on HOME_Property {\\n    currentStatus {\\n      "
           "isRecentlySold\\n      isRecentlyRented\\n      isActiveForRent\\n      isActiveForSale\\n      "
           "isOffMarket\\n      isForeclosure\\n      __typename\\n    }\\n    priceChange {\\n      "
           "priceChangeDirection\\n      __typename\\n    }\\n    activeListing {\\n      provider {\\n        "
           "summary(formatType: SHORT)\\n        extraShortSummary: summary(formatType: EXTRA_SHORT)\\n        "
           "listingSource {\\n          logoUrl\\n          __typename\\n        }\\n        __typename\\n      }\\n  "
           "    dateListed\\n      __typename\\n    }\\n    lastSold {\\n      provider {\\n        summary("
           "formatType: SHORT)\\n        extraShortSummary: summary(formatType: EXTRA_SHORT)\\n        listingSource "
           "{\\n          logoUrl\\n          __typename\\n        }\\n        __typename\\n      }\\n      "
           "__typename\\n    }\\n    providerListingId\\n    __typename\\n  }\\n  ... on HOME_FloorPlan {\\n    "
           "priceChange {\\n      priceChangeDirection\\n      __typename\\n    }\\n    provider {\\n      summary("
           "formatType: SHORT)\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment "
           "HomeDetailsCardPhotosFragment on HOME_Details {\\n  media {\\n    __typename\\n    heroImage(fallbacks: "
           "$heroImageFallbacks) {\\n      url {\\n        small\\n        medium\\n        __typename\\n      }\\n   "
           "   webpUrl: url(compression: webp) {\\n        small\\n        medium\\n        __typename\\n      }\\n   "
           "   __typename\\n    }\\n    photos {\\n      url {\\n        small\\n        medium\\n        "
           "__typename\\n      }\\n      webpUrl: url(compression: webp) {\\n        small\\n        medium\\n        "
           "__typename\\n      }\\n      __typename\\n    }\\n  }\\n  __typename\\n}\\n\\nfragment "
           "HomeDetailsCallToActionFragment on HOME_Details {\\n  hasPrequalifiers\\n  ... on HOME_Property {\\n    "
           "isTourAvailable(isOptimistic: true)\\n    __typename\\n  }\\n  leadFormCallToAction(context: CARD, "
           "appendOneClick: true) {\\n    callToActionType\\n    callToActionDisplayLabel\\n    "
           "supportsCancellableSubmission\\n    buttonStyle\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment "
           "FailedSearchFragment on SEARCH_Result {\\n  names(isInSeoLongTermRentalTitleTest: "
           "$isInSeoLongTermRentalTitleTest) {\\n    locationName\\n    __typename\\n  }\\n  location {\\n    "
           "__typename\\n    ... on SEARCH_ResultLocationPointOfInterest {\\n      exactCoordinates {\\n        "
           "latitude\\n        longitude\\n        __typename\\n      }\\n      __typename\\n    }\\n  }\\n  "
           "__typename\\n}\\n\\nfragment SearchResultsSortFragment on SEARCHDETAILS_Details {\\n  filters {\\n    "
           "sort {\\n      type\\n      ascending\\n      __typename\\n    }\\n    __typename\\n  }\\n  "
           "__typename\\n}\\n\\nfragment SingleFamilyResidenceJsonLdFragment on HOME_Property {\\n  location {\\n    "
           "partialLocation: formattedLocation(formatType: STREET_ONLY)\\n    city\\n    stateCode\\n    zipCode\\n   "
           " coordinates {\\n      latitude\\n      longitude\\n      __typename\\n    }\\n    __typename\\n  }\\n  "
           "__typename\\n}\\n\\nfragment OpenHouseDateFragment on HOME_Listing {\\n  openHouses {\\n    ... on "
           "HOME_ScheduledOpenHouse {\\n      start\\n      end\\n      startHour: formattedStartTime(format: "
           "\\\"hA\\\")\\n      endHour: formattedEndTime(format: \\\"hA\\\")\\n      __typename\\n    }\\n    "
           "__typename\\n  }\\n  __typename\\n}\\n\\nfragment OpenHouseJsonLdFragment on HOME_Details {\\n  ... on "
           "HOME_Property {\\n    url\\n    location {\\n      formattedLocation\\n      partialLocation: "
           "formattedLocation(formatType: STREET_ONLY)\\n      city\\n      stateCode\\n      zipCode\\n      "
           "coordinates {\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      __typename\\n "
           "   }\\n    activeForSaleListing {\\n      ...OpenHouseDateFragment\\n      __typename\\n    }\\n    "
           "activeForRentListing {\\n      ...OpenHouseDateFragment\\n      __typename\\n    }\\n    media {\\n      "
           "hasThreeDHome\\n      hasVideo\\n      photos {\\n        url {\\n          large\\n          "
           "__typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    price {\\n      "
           "... on HOME_SinglePrice {\\n        price\\n        currencyCode\\n        __typename\\n      }\\n      "
           "__typename\\n    }\\n    ...VirtualTourJsonLdSchemaFragment\\n    __typename\\n  }\\n  ... on "
           "HOME_RoomForRent {\\n    activeForRentListing {\\n      ...OpenHouseDateFragment\\n      __typename\\n    "
           "}\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment VirtualTourJsonLdSchemaFragment on HOME_Details "
           "{\\n  price {\\n    ... on HOME_SinglePrice {\\n      price\\n      __typename\\n    }\\n    ... on "
           "HOME_ValuationPrice {\\n      price\\n      __typename\\n    }\\n    ... on HOME_ListingSinglePrice {\\n  "
           "    price\\n      __typename\\n    }\\n    __typename\\n  }\\n  ... on HOME_Property {\\n    "
           "activeListing {\\n      provider {\\n        listingAgent {\\n          name\\n          __typename\\n    "
           "    }\\n        broker {\\n          name\\n          __typename\\n        }\\n        builder {\\n       "
           "   name\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n   "
           " __typename\\n  }\\n  __typename\\n}\\n\\nfragment CrossSellModuleFragment on SEARCH_Result {\\n  "
           "crossSellModule(variation: $crossSellVariation) {\\n    heading\\n    description\\n    ctaText\\n    "
           "ctaURL\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment SearchResultsPaginationFragment on "
           "SEARCH_Result {\\n  totalHomes\\n  currentUrl\\n  details {\\n    filters {\\n      page\\n      limit\\n "
           "     __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment "
           "SearchResultsBreadcrumbsFragment on SEARCH_Result {\\n  navigation {\\n    label\\n    url\\n    "
           "linkType\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment SearchResultsRentalJsonLdSchemaFragment "
           "on SEARCH_Result {\\n  details {\\n    searchType\\n    __typename\\n  }\\n  location {\\n    ... on "
           "SEARCH_ResultLocationCity {\\n      city\\n      state\\n      __typename\\n    }\\n    ... on "
           "SEARCH_ResultLocationState {\\n      state\\n      __typename\\n    }\\n    __typename\\n  }\\n  "
           "__typename\\n}\\n\\nfragment SearchResultsRentalResultJsonLdSchemaFragment on HOME_Property {\\n  "
           "location {\\n    city\\n    stateCode\\n    formattedLocation\\n    zipCode\\n    coordinates {\\n      "
           "latitude\\n      longitude\\n      __typename\\n    }\\n    __typename\\n  }\\n  propertyType {\\n    "
           "value\\n    __typename\\n  }\\n  currentStatus {\\n    isActiveForRent\\n    __typename\\n  }\\n  "
           "__typename\\n}\\n\\nfragment SearchResultsPopularLocationsFragment on SEARCH_Result {\\n  "
           "surroundingPopularLocations {\\n    forRent {\\n      label\\n      url\\n      __typename\\n    }\\n    "
           "forSale {\\n      label\\n      url\\n      __typename\\n    }\\n    sold {\\n      label\\n      url\\n  "
           "    __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment SearchResultsMapFragment "
           "on SEARCH_Result {\\n  mapEmptyState: emptyState(format: SHORT) {\\n    noHomesFoundText\\n    "
           "__typename\\n  }\\n  details {\\n    filters {\\n      zoom\\n      __typename\\n    }\\n    "
           "__typename\\n  }\\n  names(isInSeoLongTermRentalTitleTest: $isInSeoLongTermRentalTitleTest) {\\n    "
           "searchResultsMapTag\\n    __typename\\n  }\\n  location {\\n    boundingBox {\\n      minCoordinates {\\n "
           "       latitude\\n        longitude\\n        __typename\\n      }\\n      maxCoordinates {\\n        "
           "latitude\\n        longitude\\n        __typename\\n      }\\n      __typename\\n    }\\n    ... on "
           "SEARCH_ResultLocationCity {\\n      locationId\\n      __typename\\n    }\\n    ... on "
           "SEARCH_ResultLocationCounty {\\n      locationId\\n      __typename\\n    }\\n    ... on "
           "SEARCH_ResultLocationNeighborhood {\\n      locationId\\n      __typename\\n    }\\n    ... on "
           "SEARCH_ResultLocationPostalCode {\\n      locationId\\n      __typename\\n    }\\n    ... on "
           "SEARCH_ResultLocationState {\\n      locationId\\n      __typename\\n    }\\n    __typename\\n  }\\n  "
           "...HomeMarkerLayersContainerFragment\\n  ...HoverCardLayerFragment\\n  __typename\\n}\\n\\nfragment "
           "HomeMarkerLayersContainerFragment on SEARCH_Result {\\n  ...HomeMarkersLayerFragment\\n  "
           "__typename\\n}\\n\\nfragment HomeMarkersLayerFragment on SEARCH_Result {\\n  homes {\\n    location {\\n  "
           "    coordinates {\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      "
           "__typename\\n    }\\n    url\\n    metadata {\\n      compositeId\\n      __typename\\n    }\\n    "
           "...HomeMarkerFragment\\n    __typename\\n  }\\n  nearByHomes {\\n    ...HomeMarkerFragment\\n    "
           "__typename\\n  }\\n  __typename\\n}\\n\\nfragment HomeMarkerFragment on HOME_Details {\\n  media {\\n    "
           "hasThreeDHome\\n    __typename\\n  }\\n  location {\\n    coordinates {\\n      latitude\\n      "
           "longitude\\n      __typename\\n    }\\n    __typename\\n  }\\n  displayFlags {\\n    enableMapPin\\n    "
           "__typename\\n  }\\n  price {\\n    calloutMarkerPrice: formattedPrice(formatType: SHORT_ABBREVIATION)\\n  "
           "  __typename\\n  }\\n  url\\n  ... on HOME_Property {\\n    activeForSaleListing {\\n      openHouses {"
           "\\n        formattedDay\\n        __typename\\n      }\\n      __typename\\n    }\\n    "
           "hideMapMarkerAtZoomLevel {\\n      zoomLevel\\n      hide\\n      __typename\\n    }\\n    __typename\\n  "
           "}\\n  ... on HOME_RentalCommunity {\\n    hideMapMarkerAtZoomLevel {\\n      zoomLevel\\n      hide\\n    "
           "  __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment HoverCardLayerFragment on "
           "SEARCH_Result {\\n  homes {\\n    ...HomeHoverCardFragment\\n    __typename\\n  }\\n  nearByHomes {\\n    "
           "...HomeHoverCardFragment\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment HomeHoverCardFragment on "
           "HOME_Details {\\n  ...HomeDetailsCardFragment\\n  ...HomeDetailsCardHeroFragment\\n  "
           "...HomeDetailsCardPhotosFragment\\n  location {\\n    coordinates {\\n      latitude\\n      longitude\\n "
           "     __typename\\n    }\\n    __typename\\n  }\\n  displayFlags {\\n    enableMapPin\\n    "
           "showMLSLogoOnMapMarkerCard\\n    __typename\\n  }\\n  preferences {\\n    isHomePreviouslyViewed\\n    "
           "__typename\\n  }\\n  __typename\\n}\\n\\nfragment HomeDetailsCardHeroFragment on HOME_Details {\\n  media "
           "{\\n    heroImage(fallbacks: $heroImageFallbacks) {\\n      url {\\n        small\\n        medium\\n     "
           "   __typename\\n      }\\n      webpUrl: url(compression: webp) {\\n        small\\n        __typename\\n "
           "     }\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment "
           "SearchResultsFiltersFragment on SEARCH_Result {\\n  transitSystems {\\n    name\\n    iconUrl(format: "
           "SVG)\\n    isSelected\\n    filterLabel\\n    __typename\\n  }\\n  homeCounts {\\n    agentListingsCount "
           "{\\n      formattedValue\\n      __typename\\n    }\\n    otherListingsCount {\\n      formattedValue\\n  "
           "    __typename\\n    }\\n    resultCount {\\n      formattedValue\\n      __typename\\n    }\\n    "
           "__typename\\n  }\\n  dynamicFilters {\\n    homeTypes {\\n      name\\n      searchUrl\\n      "
           "__typename\\n    }\\n    listingTypes {\\n      name\\n      searchUrl\\n      __typename\\n    }\\n    "
           "__typename\\n  }\\n  details {\\n    searchType\\n    ...SearchResultsSortFragment\\n    filters {\\n     "
           " isAlternateListingSource\\n      price {\\n        min\\n        max\\n        __typename\\n      }\\n   "
           "   bedrooms {\\n        min\\n        max\\n        __typename\\n      }\\n      bathrooms {\\n        "
           "min\\n        max\\n        __typename\\n      }\\n      squareFeet {\\n        min\\n        max\\n      "
           "  __typename\\n      }\\n      hoaFee {\\n        min\\n        max\\n        __typename\\n      }\\n     "
           " propertyTypes\\n      lotSize {\\n        min\\n        max\\n        __typename\\n      }\\n      "
           "mlsId\\n      newListing {\\n        range {\\n          min\\n          max\\n          timestamp\\n     "
           "     __typename\\n        }\\n        daysAgo\\n        __typename\\n      }\\n      recentlyReduced {\\n "
           "       range {\\n          min\\n          max\\n          timestamp\\n          __typename\\n        "
           "}\\n        daysAgo\\n        __typename\\n      }\\n      openHomes {\\n        range {\\n          "
           "min\\n          max\\n          timestamp\\n          __typename\\n        }\\n        type\\n        "
           "__typename\\n      }\\n      yearBuilt {\\n        min\\n        max\\n        __typename\\n      }\\n    "
           "  keywords\\n      listingTypes\\n      plus55Communities {\\n        exclude\\n        __typename\\n     "
           " }\\n      airConditioning {\\n        has\\n        __typename\\n      }\\n      soldWithin\\n      "
           "pets\\n      furnished\\n      rentalListingTags\\n      isInverseSearch\\n      __typename\\n    }\\n    "
           "__typename\\n  }\\n  __typename\\n}\\n\\nfragment SearchResultsProviderAttributionFragment on "
           "SEARCH_Result {\\n  providers {\\n    listingSource {\\n      logoUrl\\n      attribution\\n      "
           "alternativeSources {\\n        name\\n        url\\n        __typename\\n      }\\n      disclaimer {\\n  "
           "      markdown\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n  "
           "__typename\\n}\\n\\nfragment SearchResultsMarketDetailsFragment on SEARCH_Result {\\n  details {\\n    "
           "location {\\n      cities {\\n        city\\n        state\\n        __typename\\n      }\\n      "
           "__typename\\n    }\\n    __typename\\n  }\\n  seoTests {\\n    name\\n    isActive\\n    __typename\\n  "
           "}\\n  ...SearchResultsNeighborhoodsListFragment\\n  ...MarketInsightsDataFragment\\n  "
           "...SearchResultsSummaryFragment\\n  ...SearchResultsWhatLocalsSayFragment\\n  "
           "__typename\\n}\\n\\nfragment SearchResultsNeighborhoodsListFragment on SEARCH_Result {\\n  surroundings("
           "limit: 15) {\\n    ...NeighborhoodCardFragment\\n    ... on SURROUNDINGS_Neighborhood {\\n      "
           "neighborhoodAttribution\\n      __typename\\n    }\\n    __typename\\n  }\\n  "
           "__typename\\n}\\n\\nfragment NeighborhoodCardFragment on SURROUNDINGS_Neighborhood {\\n  name\\n  "
           "ndpActive\\n  ndpUrl\\n  media(includeStoryMedia: false) {\\n    heroImage {\\n      ... on "
           "MEDIA_HeroImageMap {\\n        url {\\n          path: custom(size: {width: 136, height: 136, "
           "cropMode: fill}, zoomLevel: 1100)\\n          __typename\\n        }\\n        __typename\\n      }\\n    "
           "  ... on MEDIA_HeroImageStory {\\n        url {\\n          path: custom(size: {width: 136, height: 136, "
           "cropMode: fill})\\n          __typename\\n        }\\n        __typename\\n      }\\n      ... on "
           "MEDIA_HeroImagePhoto {\\n        url {\\n          path: custom(size: {width: 136, height: 136, "
           "cropMode: fill})\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n  "
           "  }\\n    __typename\\n  }\\n  localFacts {\\n    forSaleStats {\\n      min\\n      max\\n      "
           "__typename\\n    }\\n    homesForSaleCount\\n    forRentStats {\\n      min\\n      max\\n      "
           "__typename\\n    }\\n    homesForRentCount\\n    soldHomesStats {\\n      min\\n      max\\n      "
           "__typename\\n    }\\n    soldHomesCount\\n    __typename\\n  }\\n  neighborhoodSearchUrlCTA {\\n    "
           "forSale\\n    forRent\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment "
           "SearchResultsWhatLocalsSayFragment on SEARCH_Result {\\n  searchLocationSurroundings {\\n    "
           "locationId\\n    name\\n    ... on SURROUNDINGS_Neighborhood {\\n      ndpType\\n      ndpUrl\\n      "
           "name\\n      ndpActive\\n      localUGC {\\n        ... on SURROUNDINGS_LocalUGC {\\n          "
           "...LocalUGCFragment\\n          __typename\\n        }\\n        __typename\\n      }\\n      "
           "__typename\\n    }\\n    ... on SURROUNDINGS_City {\\n      localUGC {\\n        ... on "
           "SURROUNDINGS_LocalUGC {\\n          ...LocalUGCFragment\\n          __typename\\n        }\\n        "
           "__typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment "
           "LocalUGCFragment on SURROUNDINGS_LocalUGC {\\n  title\\n  localReviews {\\n    categories {\\n      id\\n "
           "     displayName\\n      reviewCount\\n      callToAction\\n      __typename\\n    }\\n    "
           "totalReviews\\n    reviews(limitPerCategory: 8) {\\n      id\\n      reviewer {\\n        name\\n        "
           "__typename\\n      }\\n      text\\n      context {\\n        displayName\\n        __typename\\n      "
           "}\\n      category {\\n        id\\n        displayName\\n        __typename\\n      }\\n      "
           "dateCreated\\n      reactionSummary {\\n        counts {\\n          helpful\\n          __typename\\n    "
           "    }\\n        viewerReactions {\\n          helpful\\n          __typename\\n        }\\n        "
           "__typename\\n      }\\n      flagSummary {\\n        totalCount\\n        __typename\\n      }\\n      "
           "__typename\\n    }\\n    __typename\\n  }\\n  reviewHighlights @include(if: $includeReviewHighlights) {"
           "\\n    regionId\\n    text\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment "
           "SearchResultsSummaryFragment on SEARCH_Result {\\n  marketInsights(sourceAllFromZHVI: true) {\\n    "
           "rentalMarketInsights {\\n      medianRentalPriceAverageForPastYear\\n      __typename\\n    }\\n    "
           "__typename\\n  }\\n  __typename\\n}\\n\\nfragment MarketInsightsDataFragment on SEARCH_Result {\\n  "
           "names(isInSeoLongTermRentalTitleTest: $isInSeoLongTermRentalTitleTest) {\\n    locationName\\n    "
           "__typename\\n  }\\n  marketInsights(sourceAllFromZHVI: true) {\\n    homeStatsByBedroomCount: "
           "statsByHomeFeature(featureType: BEDROOMS) {\\n      displayName\\n      featureStats {\\n        "
           "displayName\\n        homeValueIndexPrice\\n        inventorySummary @include(if: "
           "$isNearbyCitiesEnabled)\\n        ... on STATS_AND_TRENDS_HomeFeatureStat {\\n          "
           "forSaleSearchUrl\\n          __typename\\n        }\\n        __typename\\n      }\\n      summary {\\n   "
           "     summaryDescription\\n        newListingsSearchUrl\\n        newListingsSearchCta\\n        "
           "__typename\\n      }\\n      __typename\\n    }\\n    affordability {\\n      name\\n      summary\\n     "
           " trend {\\n        value\\n        formattedValue\\n        date\\n        formattedDate(dateFormat: "
           "\\\"MMMM YYYY\\\")\\n        __typename\\n      }\\n      __typename\\n    }\\n    "
           "affordabilityAttribution\\n    propertyCountByFeaturesAndStyles: statsByHomeFeature(\\n      featureType: "
           "POPULAR_FEATURES\\n    ) {\\n      displayName\\n      featureStats {\\n        displayName\\n        "
           "inventorySummary\\n        forSaleSearchUrl\\n        __typename\\n      }\\n      __typename\\n    }\\n  "
           "  __typename\\n  }\\n  surroundings(limit: 15) {\\n    ... on SURROUNDINGS_Neighborhood {\\n      name\\n "
           "     forSaleNeighborhoodSearchCanonicalURL\\n      localFacts {\\n        homesForSaleCount\\n        "
           "__typename\\n      }\\n      __typename\\n    }\\n    ... on SURROUNDINGS_City @include(if: "
           "$isNearbyCitiesEnabled) {\\n      __typename\\n      name\\n      media {\\n        heroImage {\\n        "
           "  url {\\n            small\\n            __typename\\n          }\\n          __typename\\n        }\\n  "
           "      __typename\\n      }\\n      localFacts {\\n        forSaleStats {\\n          "
           "formattedPriceRange\\n          __typename\\n        }\\n        homesForSaleCount\\n        "
           "__typename\\n      }\\n      searchUrl {\\n        forSale\\n        __typename\\n      }\\n    }\\n    "
           "__typename\\n  }\\n  __typename\\n}\\n\\nfragment SearchResultsFooterCardFragment on SEARCH_Result {\\n  "
           "homes {\\n    ...HomeDetailsCardFragment\\n    ...HomeDetailsCardPhotosFragment\\n    __typename\\n  }\\n "
           " __typename\\n}\\n\\nfragment SearchDetailsFragment on SEARCHDETAILS_Details {\\n  searchType\\n  "
           "location {\\n    cities {\\n      city\\n      state\\n      __typename\\n    }\\n    states {\\n      "
           "state\\n      __typename\\n    }\\n    counties\\n    neighborhoods\\n    neighborhoodRegions {\\n      "
           "name\\n      regionId\\n      locationId\\n      __typename\\n    }\\n    zips\\n    schoolDistricts\\n   "
           " university {\\n      id\\n      name\\n      __typename\\n    }\\n    school {\\n      id\\n      "
           "name\\n      __typename\\n    }\\n    customArea {\\n      latLngs {\\n        latitude\\n        "
           "longitude\\n        __typename\\n      }\\n      encodedPolygon\\n      __typename\\n    }\\n    commute "
           "{\\n      type\\n      maxTime\\n      polygons {\\n        latitude\\n        longitude\\n        "
           "__typename\\n      }\\n      label\\n      __typename\\n    }\\n    pointOfInterest {\\n      latitude\\n "
           "     longitude\\n      __typename\\n    }\\n    coordinates {\\n      center {\\n        latitude\\n      "
           "  longitude\\n        __typename\\n      }\\n      southEast {\\n        latitude\\n        longitude\\n  "
           "      __typename\\n      }\\n      northEast {\\n        latitude\\n        longitude\\n        "
           "__typename\\n      }\\n      southWest {\\n        latitude\\n        longitude\\n        __typename\\n   "
           "   }\\n      northWest {\\n        latitude\\n        longitude\\n        __typename\\n      }\\n      "
           "__typename\\n    }\\n    radiusSize\\n    __typename\\n  }\\n  filters {\\n    "
           "isAlternateListingSource\\n    bedrooms {\\n      min\\n      max\\n      __typename\\n    }\\n    "
           "bathrooms {\\n      min\\n      max\\n      __typename\\n    }\\n    price {\\n      min\\n      max\\n   "
           "   __typename\\n    }\\n    squareFeet {\\n      min\\n      max\\n      __typename\\n    }\\n    zoom\\n "
           "   street\\n    propertyTypes\\n    lotSize {\\n      min\\n      max\\n      __typename\\n    }\\n    "
           "hoaFee {\\n      min\\n      max\\n      __typename\\n    }\\n    mlsId\\n    newListing {\\n      range "
           "{\\n        min\\n        max\\n        timestamp\\n        __typename\\n      }\\n      daysAgo\\n      "
           "__typename\\n    }\\n    openHomes {\\n      range {\\n        min\\n        max\\n        timestamp\\n   "
           "     __typename\\n      }\\n      __typename\\n    }\\n    percentChanged\\n    recentlyReduced {\\n      "
           "range {\\n        min\\n        max\\n        timestamp\\n        __typename\\n      }\\n      daysAgo\\n "
           "     __typename\\n    }\\n    pricePerSquareFoot {\\n      min\\n      max\\n      __typename\\n    }\\n  "
           "  yearBuilt {\\n      min\\n      max\\n      __typename\\n    }\\n    keywords\\n    listingTypes\\n    "
           "foreclosureTypes\\n    discoveryGroup\\n    sort {\\n      type\\n      ascending\\n      __typename\\n   "
           " }\\n    soldWithin\\n    pets\\n    brokerFee\\n    buildingAmenities\\n    unitAmenities\\n    "
           "furnished\\n    rentalListingTags\\n    landlordPays\\n    page\\n    offset\\n    limit\\n    transit {"
           "\\n      system\\n      line\\n      station\\n      __typename\\n    }\\n    includeOffMarket\\n    "
           "isAlternateListingSource\\n    propertyAmenityTypes\\n    shortcutSearch\\n    isInverseSearch\\n    "
           "plus55Communities {\\n      exclude\\n      __typename\\n    }\\n    airConditioning {\\n      has\\n     "
           " __typename\\n    }\\n    sceneryTypes\\n    __typename\\n  }\\n  canonicalUrl\\n  description\\n  "
           "__typename\\n}\\n\\nfragment ExploreCollectionsFragmentBot on SEARCH_Result {\\n  exploreCollections("
           "prefetch: false) {\\n    ...ExploreCollectionsFragment\\n    __typename\\n  }\\n  "
           "__typename\\n}\\n\\nfragment ExploreCollectionsFragment on SEARCH_ExploreCollection {\\n  title\\n  "
           "categories\\n  id\\n  position\\n  searches {\\n    title\\n    subTitle\\n    disclaimer\\n    "
           "subTitleFormattedFilterLists\\n    ctaText\\n    searchUrl\\n    homes {\\n      location {\\n        "
           "coordinates {\\n          latitude\\n          longitude\\n          __typename\\n        }\\n        "
           "__typename\\n      }\\n      ...HomeDetailsCardFragment\\n      ...HomeDetailsCardHeroFragment\\n      "
           "...HomeDetailsCardPhotosFragment\\n      __typename\\n    }\\n    __typename\\n  }\\n  "
           "__typename\\n}\\n\\nfragment HiddenHomeSrpFragment on HOME_Details {\\n  isHideable\\n  typedHomeId\\n  "
           "__typename\\n}\",\"variables\":{\"defaultSortType\":null,\"defaultSortDirection\":null,"
           "\"includeNearBy\":true,\"isNearbyCitiesEnabled\":false,\"inFooterTest\":false,\"inCrossSellTest\":false,"
           "\"includeReviewHighlights\":true,\"heroImageFallbacks\":[\"STREET_VIEW\",\"SATELLITE_VIEW\"],"
           "\"searchDetails\":{\"searchType\":\"FOR_SALE\",\"location\":{\"cities\":[{\"city\":\"Atlanta\","
           "\"state\":\"GA\"}],\"coordinates\":{\"southWest\":{\"latitude\":32.78025940356588,"
           "\"longitude\":-84.82683329147177},\"northEast\":{\"latitude\":34.54267636072575,"
           "\"longitude\":-83.68974833053427},\"southEast\":{\"latitude\":32.78025940356588,"
           "\"longitude\":-83.68974833053427},\"northWest\":{\"latitude\":34.54267636072575,"
           "\"longitude\":-84.82683329147177},\"center\":{\"latitude\":33.665981220094615,"
           "\"longitude\":-84.25829081100302}}},\"filters\":{\"sort\":{\"type\":\"DATE\",\"ascending\":false},"
           "\"page\":1,\"limit\":40,\"zoom\":9,\"isAlternateListingSource\":false,\"propertyTypes\":[],"
           "\"listingTypes\":[],\"pets\":[],\"rentalListingTags\":[],\"foreclosureTypes\":[],\"buildingAmenities\":["
           "],\"unitAmenities\":[],\"landlordPays\":[],\"propertyAmenityTypes\":[],\"sceneryTypes\":[]}},"
           "\"isBot\":false,\"crossSellVariation\":\"VARIATION_2\"}}")

# Set your CSRF token here directly
csrf_token = 'AAigUxLeI7edVJsfonGpPYmKX/u3vRvwzRa3q7ns'  # Replace this with your actual CSRF token

all_homes = get_all_trulia_data(initial_payload, csrf_token)

print(f"\nTotal homes fetched: {len(all_homes)}")

# Save the data to a CSV file
csv_filename = 'trulia_homes_data.csv'
save_to_csv(all_homes, csv_filename)

print(f"Data saved to {csv_filename}")
print("\nData extraction complete.")
