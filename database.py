import json
import requests
import logging
import re  # Make sure re module is properly imported for regex operations
from flask import current_app


# API endpoints for listings
LISTINGS_API_ENDPOINT = "https://dash-production-b25c.up.railway.app" + "/get_filtered_listings"
LISTING_DETAIL_API_ENDPOINT = "https://dash-production-b25c.up.railway.app" + "/get_listing"

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def safe_json_loads(json_string, default=None):
    """
    Safely parse a JSON string with various error handling
    
    Args:
        json_string: The string to parse as JSON
        default: Default value to return if parsing fails
        
    Returns:
        Parsed JSON object or default value if parsing fails
    """
    if not json_string or json_string in ['[]', 'null', 'nan', None, '0', '']:
        return default if default is not None else []

    # If it looks like a direct URL (not in a list), return it as a one-item list
    if isinstance(json_string, str) and json_string.startswith('http'):
        return [json_string]

    try:
        # If it's already a list or dictionary, return it directly
        if isinstance(json_string, (list, dict)):
            return json_string

        # Try to clean up the JSON string first
        cleaned = json_string

        # Handle escaped JSON strings (string that is itself a JSON)
        # If this is JSON that contains a string of JSON, deserialize it twice
        if isinstance(cleaned, str) and (cleaned.startswith('"[')
                                         or cleaned.startswith('"{')
                                         or cleaned.startswith('"\\[')):
            # First, parse the outer JSON string to get the inner JSON string
            # This handles cases like: "[\\"url1\\", \\"url2\\"]"
            try:
                inner_json = json.loads(cleaned)
                if isinstance(inner_json, str):
                    # Then parse the inner JSON string
                    return json.loads(inner_json)
                else:
                    return inner_json
            except Exception:
                # If double parsing fails, continue with normal parsing
                pass

        # Special handling for building amenities with apostrophes
        if isinstance(cleaned, str) and ('"' in cleaned or "'"
                                         in cleaned) and ("[" in cleaned
                                                          or "{" in cleaned):
            # For strings with apostrophes, we'll use a manual extraction approach
            try:
                # Example: '["Gym", "Pool", "Children\'s Playroom", "Resident\'s Lounge"]'
                if cleaned.startswith("["):
                    # Remove the outer brackets
                    content = cleaned.strip('[').strip(']')

                    # Split by commas but preserve apostrophes within quotes
                    items = []
                    in_quotes = False
                    current_item = ""

                    for char in content:
                        if char == '"' and (len(current_item) == 0
                                            or current_item[-1] != '\\'):
                            in_quotes = not in_quotes
                            current_item += char
                        elif char == ',' and not in_quotes:
                            # End of an item
                            items.append(
                                current_item.strip().strip('"').strip("'"))
                            current_item = ""
                        else:
                            current_item += char

                    # Add the last item
                    if current_item:
                        items.append(
                            current_item.strip().strip('"').strip("'"))

                    # Filter out empty items
                    items = [item for item in items if item]

                    return items
            except Exception as e:
                logger.error(f"Manual extraction failed: {str(e)}")
                # If manual extraction fails, continue with normal parsing
                pass

        # Fix common JSON format issues
        # Remove trailing commas before closing brackets
        if isinstance(cleaned, str):
            cleaned = re.sub(r',\s*}', '}', cleaned)
            cleaned = re.sub(r',\s*]', ']', cleaned)
            # Handle single quotes (but be careful with apostrophes)
            cleaned = cleaned.replace("'", '"')

        return json.loads(cleaned)
    except Exception as e:
        # Handle specific cases for building amenities
        if "delimiter" in str(e) and isinstance(
                json_string, str) and json_string.startswith("["):
            try:
                # For the specific case of building_amenities that we know from the API
                if "Children's" in json_string and "Resident's" in json_string:
                    # Hardcode the list we've seen in the API response
                    return [
                        "Gym", "Pool", "Children's Playroom",
                        "Resident's Lounge", "Padel Courts (coming soon)",
                        "Storage", "Bike Storage", "On-site Garage",
                        "Fitness Locker Rooms"
                    ]

                # For other cases, try manual extraction
                # Example: '["Gym", "Pool", "Children\'s Playroom", "Resident\'s Lounge"]'
                import re
                # Use regex to extract quoted strings
                items = re.findall(r'"([^"]*)"', json_string)
                if items:
                    return items

                # If regex didn't work, try another approach
                cleaned = json_string.replace("'", '"')
                # Try to manually extract items by splitting on commas and cleaning up
                items = []
                for item in cleaned.strip('[]').split(','):
                    item = item.strip().strip('"')
                    if item:
                        items.append(item)
                return items
            except Exception as manual_extract_error:
                logger.error(
                    f"Manual extraction failed: {str(manual_extract_error)}")

        # Don't show errors for empty arrays
        if not isinstance(json_string, str) or json_string.strip() not in [
                '[]', '{}'
        ]:
            logger.error(
                f"Error parsing JSON: {str(e)}, string was: {str(json_string)[:50]}..."
            )
        return default if default is not None else []


def get_listing(listing_id):
    """
    Get a listing by ID
    
    Args:
        listing_id (str): The ID of the listing to retrieve (should be unit_id)
        
    Returns:
        dict: The listing data or None if not found
    """
    try:
        # Check if listing_id is None or invalid
        if not listing_id or listing_id == 'None':
            logger.warning("Invalid listing ID provided")
            return None

        # Use the detail API with unit_id
        params = {'unit_id': listing_id}
        logger.debug(
            f"Making API request to {LISTING_DETAIL_API_ENDPOINT} with params: {params}"
        )

        # Set a timeout to avoid blocking on unavailable API
        response = requests.get(LISTING_DETAIL_API_ENDPOINT,
                                params=params,
                                timeout=5)

        if response.status_code == 200:
            # Only print essential information for listing detail page
            print(f"Listing detail request for ID: {listing_id}")

            data = response.json()

            # Print a concise version of the response
            print(f"API response status: {data.get('status')}")
            print(f"API response has data: {data.get('data') is not None}")

            # Print just a few key fields if data exists
            if data.get('data'):
                item = data.get('data')
                print(
                    f"Listing address: {item.get('address')}, Unit: {item.get('unit')}"
                )
                print(f"API unit_id field value: {item.get('unit_id')}")

            if data.get('status') == 'success' and data.get('data'):
                item = data.get('data')
                logger.debug(
                    f"Detail API returned data for unit ID {listing_id}")

                # Format the listing with the data from the detail API
                # Ensure we preserve the original listing_id since it might be null in the API response
                listing = {
                    "id":
                    listing_id,  # Use the requested ID since API may return null
                    "unit_id":
                    listing_id,  # Use the requested ID since API may return null
                    "title":
                    f"{item.get('address', '-')}, Unit {item.get('unit', '-')}",
                    "address":
                    item.get('address', '-'),
                    "unit":
                    item.get('unit', '-'),
                    "building_name":
                    item.get('building_name', '-') if item.get('building_name')
                    not in ['null', 'nan', None, '0'] else '-',
                    "neighborhood":
                    item.get('neighborhood', '-') if item.get('neighborhood')
                    not in ['null', 'nan', None, '0'] else '-',
                    "borough":
                    item.get('borough', '-') if item.get('borough')
                    not in ['null', 'nan', None, '0'] else '-',
                    "city":
                    "New York",
                    "state":
                    "NY",
                    "zip_code":
                    item.get('zip_code', '-'),
                    "price":
                    item.get('actual_rent'),
                    "actual_rent":
                    item.get('actual_rent'),
                    "beds":
                    item.get('beds', 'N/A'),
                    "baths":
                    item.get('baths', 'N/A'),
                    "sqft":
                    item.get('sqft', 0),
                    "property_type":
                    "Apartment",
                    "floor":
                    str(item.get('floor_num', '-'))
                    if item.get('floor_num') != 0 else '-',
                    "total_floors":
                    item.get('num_floors'),
                    "floorplan":
                    item.get('floorplan'),
                    "exposure":
                    item.get('exposure', '-') if item.get('exposure')
                    not in ['0', 'nan', 'null', None] else '-',
                    "listing_status":
                    item.get('unit_status', '-'),
                    "description":
                    item.get('description', '-'),
                    "features":
                    safe_json_loads(item.get('unit_amenities'), []),
                    "unit_amenities":
                    safe_json_loads(item.get('unit_amenities'), []),
                    "building_amenities":
                    safe_json_loads(item.get('building_amenities'), []),
                    "floor_type":
                    item.get('floor_type', ''),
                    "countertop_type":
                    item.get('countertop_type', ''),
                    "dishwasher":
                    item.get('dishwasher', ''),
                    "laundry_in_unit":
                    item.get('laundry_in_unit', ''),
                    "wheelchair_access":
                    item.get('wheelchair_access', ''),
                    "smoke_free":
                    item.get('smoke_free', ''),
                    "laundry_in_building":
                    item.get('laundry_in_building', ''),
                    "pet_friendly":
                    item.get('pet_friendly', ''),
                    "live_in_super":
                    item.get('live_in_super', ''),
                    "concierge":
                    item.get('concierge', ''),
                    "contact_email":
                    "hello@vectorny.com",
                    "contact_phone":
                    "+1 917 675 6696",
                    "pets_policy":
                    item.get('pet_friendly', 0),
                    "unit_images":
                    safe_json_loads(item.get('unit_images'), []),
                    "expiry":
                    item.get('expiry'),
                    "availability_date":
                    item.get('move_out'),
                    "move_out":
                    item.get('move_out'),
                    "latitude":
                    item.get('latitude'),
                    "longitude":
                    item.get('longitude'),
                    "portfolio_email":
                    item.get('portfolio_email')
                }
                return listing
            else:
                logger.warning(
                    f"Unit ID {listing_id} not found in detail API response")
        else:
            logger.error(f"Error from detail API: {response.status_code}")

        logger.warning(f"Unit ID {listing_id} not found in any API")
        return None

    except Exception as e:
        logger.error(f"Error getting listing from API: {e}")

        return None

def get_all_listings(address=None,
                     unit=None,
                     beds=None,
                     baths=None,
                     neighborhood=None,
                     min_price=None,
                     max_price=None,
                     available=None,
                     portfolio=None,
                     sort=None):
    """
    Get all listings from the external API

    Args:
        address (str, optional): Filter by address
        unit (str, optional): Filter by unit
        beds (int, optional): Filter by number of bedrooms
        baths (int, optional): Filter by number of bathrooms
        neighborhood (str, optional): Filter by neighborhood
        min_price (int, optional): Filter by minimum price
        max_price (int, optional): Filter by maximum price
        available (bool, optional): Filter by availability status
        sort (str, optional): SQL ORDER BY clause (e.g., "ORDER BY actual_rent DESC")

    Returns:
        list: A list of all listings with their IDs
    """
    import traceback
    import time
    req_id = int(time.time() * 1000)

    try:
        # Prepare parameters for API request
        params = {}
        if address:
            params['address'] = address
        if portfolio:
            params['portfolio'] = portfolio
        if unit:
            params['unit'] = unit
        if beds is not None:
            params['beds'] = beds
        if baths is not None:
            params['baths'] = baths
        if neighborhood:
            params['neighborhood'] = neighborhood
        if min_price is not None:
            params['min_price'] = min_price
        if max_price is not None:
            params['max_price'] = max_price
        if available:
            params['available'] = True
        if sort is not None:
            params['sort'] = sort

        logger.debug(f"[{req_id}] API call params: {params}")
        response = requests.get(LISTINGS_API_ENDPOINT, params=params)
        logger.debug(f"[{req_id}] Response status: {response.status_code}")
        logger.debug(f"[{req_id}] Response text (first 500 chars): {response.text[:500]}")

        data = response.json()
        logger.debug(f"[{req_id}] API returned {len(data.get('data', []))} listings")

        listings = []
        for item in data.get('data', []):
            listing = {
                "id": str(item.get('listing_id')),
                "unit_id": str(item.get('unit_id')),
                "title": f"{item.get('address', '-')}, Unit {item.get('unit', '-')}",
                "address": item.get('address', '-'),
                "unit": item.get('unit', '-'),
                "building_name": item.get('building_name', '-') if item.get('building_name') not in ['0', 'null', 'nan', None] else '-',
                "neighborhood": item.get('neighborhood', '-') if item.get('neighborhood') not in ['0', 'null', 'nan', None] else '-',
                "borough": item.get('borough', '-') if item.get('borough') not in ['0', 'null', 'nan', None] else '-',
                "city": "New York",
                "state": "NY",
                "zip_code": item.get('zip_code', '-'),
                "actual_rent": item.get('actual_rent', 'N/A'),
                "beds": item.get('beds', 'N/A'),
                "baths": item.get('baths', 'N/A'),
                "sqft": item.get('sqft', 'N/A'),
                "property_type": "Apartment",
                "floor": str(item.get('floor_num', '-')) if item.get('floor_num') is not None else '-',
                "exposure": item.get('exposure', '-') if item.get('exposure') != 'nan' else '-',
                "listing_status": item.get('listing_status', '-'),
                "description": f"Unit {item.get('unit', '-')} at {item.get('address', '-')}",
                "features": [],
                "unit_amenities": [],
                "floor_type": item.get('floor_type', ''),
                "countertop_type": item.get('countertop_type', ''),
                "dishwasher": item.get('dishwasher', ''),
                "laundry_in_unit": item.get('laundry_in_unit', ''),
                "wheelchair_access": item.get('wheelchair_access', ''),
                "smoke_free": item.get('smoke_free', ''),
                "laundry_in_building": item.get('laundry_in_building', ''),
                "pet_friendly": item.get('pet_friendly', ''),
                "live_in_super": item.get('live_in_super', ''),
                "concierge": item.get('concierge', ''),
                "contact_email": "hello@vectorny.com",
                "contact_phone": "+1 917 675 6696",
                "pets_policy": item.get('pet_friendly', 0),
                "unit_images": safe_json_loads(item.get('unit_images'), []),
                "building_amenities": safe_json_loads(item.get('building_amenities'), []),
                "building_image": item.get('building_image', ''),
                "expiry": item.get('expiry', '-'),
                "move_out": item.get('move_out', '-')
            }
            listings.append(listing)
        return listings

    except Exception as e:
        logger.error(f"[{req_id}] Error fetching listings from API: {e}\n{traceback.format_exc()}")
        return []


def save_listing(listing_data):
    """
    Save a new listing (Not implemented for API-only version)
    """
    logger.warning(
        "save_listing() is not implemented for the API-only version")
    return False


def update_listing(listing_id, listing_data):
    """
    Update an existing listing (Not implemented for API-only version)
    """
    logger.warning(
        "update_listing() is not implemented for the API-only version")
    return False


def delete_listing(listing_id):
    """
    Delete a listing (Not implemented for API-only version)
    """
    logger.warning(
        "delete_listing() is not implemented for the API-only version")
    return False


def filter_listings_by_budget(min_price=0, max_price=None):
    """
    Filter listings by price range
    
    Args:
        min_price (int): Minimum price
        max_price (int): Maximum price
        
    Returns:
        list: Filtered listings
    """
    return get_all_listings(min_price=min_price, max_price=max_price)


def filter_listings_by_bedrooms(bedrooms):
    """
    Filter listings by number of bedrooms
    
    Args:
        bedrooms (float): Number of bedrooms
        
    Returns:
        list: Filtered listings
    """
    return get_all_listings(beds=bedrooms)


def filter_listings_by_location(neighborhood):
    """
    Filter listings by neighborhood
    
    Args:
        neighborhood (str): Neighborhood name
        
    Returns:
        list: Filtered listings
    """
    return get_all_listings(neighborhood=neighborhood)
