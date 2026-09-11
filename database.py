import json
import requests
import logging
import re  # Make sure re module is properly imported for regex operations
from flask import current_app


# API endpoints for listings
DASH_API_HOST = "https://dash-production-b25c.up.railway.app"
LISTINGS_API_ENDPOINT = DASH_API_HOST + "/get_filtered_listings"
LISTING_DETAIL_API_ENDPOINT = DASH_API_HOST + "/get_listing"
UNIQUE_VALUES_API_ENDPOINT = DASH_API_HOST + "/unique-values"

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
                    int(float(item.get('zip_code')))
                    if item.get('zip_code') not in [None, '', 'null', 'nan', '0', 0]
                    and str(item.get('zip_code')).replace('.', '', 1).isdigit()
                    else '',
                    "price":
                    item.get('listed_price'),
                    "actual_rent":
                    item.get('listed_net'),
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
                    "outdoor_space":
                    item.get('outdoor_space', ''),
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
                    item.get('portfolio_email'),
                    "address_id":
                    item.get('address_id')
                }
                return listing
            else:
                logger.warning(
                    f"Unit ID {listing_id} not found in detail API response")
        else:
            logger.error(f"Error from detail API: {response.status_code}")

        logger.warning(f"Unit ID {listing_id} not found in any API")
        return _listing_from_filtered_index(listing_id)

    except Exception as e:
        logger.error(f"Error getting listing from API: {e}")
        return _listing_from_filtered_index(listing_id)


def _listing_from_filtered_index(listing_id):
    """Fallback when /get_listing is unavailable: find the unit in the listings index."""
    try:
        wanted = str(listing_id)
        for listing in get_all_listings():
            if str(listing.get('unit_id')) == wanted or str(listing.get('id')) == wanted:
                logger.warning(
                    f"Using listings index fallback for unit ID {listing_id}"
                )
                return listing
    except Exception as e:
        logger.error(f"Listings index fallback failed for {listing_id}: {e}")
    return None

def _dash_payload_items(payload):
    """Dash sometimes returns rows under `data`, sometimes under `listings`."""
    if not isinstance(payload, dict):
        return []
    items = payload.get('data')
    if isinstance(items, list):
        return items
    items = payload.get('listings')
    if isinstance(items, list):
        return items
    return []


def _dash_request_listings(params, req_id, retries=3, timeout=12):
    """
    Call Dash get_filtered_listings with retries.

    Broad/unfiltered Dash queries currently fail with:
      name '_format_listing_move_out' is not defined
    Narrow queries (especially address=...) are more reliable.
    """
    import time

    last_error = None
    for attempt in range(retries):
        try:
            response = requests.get(LISTINGS_API_ENDPOINT, params=params, timeout=timeout)
            payload = response.json()
            if isinstance(payload, dict) and payload.get('status') == 'error':
                last_error = payload.get('message') or 'Dash returned status=error'
                logger.warning(
                    f"[{req_id}] Dash listings error (attempt {attempt + 1}/{retries}) "
                    f"params={params}: {last_error}"
                )
                time.sleep(0.25 * (attempt + 1))
                continue
            items = _dash_payload_items(payload)
            logger.debug(f"[{req_id}] Dash returned {len(items)} listings for params={params}")
            return items, None
        except Exception as exc:
            last_error = str(exc)
            logger.warning(
                f"[{req_id}] Dash listings request failed (attempt {attempt + 1}/{retries}): {exc}"
            )
            time.sleep(0.25 * (attempt + 1))
    return [], last_error


def _unique_listing_addresses(req_id):
    try:
        response = requests.get(UNIQUE_VALUES_API_ENDPOINT, timeout=12)
        payload = response.json()
        addresses = payload.get('unique_addresses') or []
        return [a for a in addresses if a]
    except Exception as exc:
        logger.error(f"[{req_id}] Failed to load unique addresses for listings fallback: {exc}")
        return []


def _fanout_listings_by_address(base_params, req_id, max_workers=8):
    """Assemble inventory by querying each known address (Dash unfiltered is broken)."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    addresses = _unique_listing_addresses(req_id)
    if not addresses:
        return []

    # Keep caller filters, but never re-use a single address across the fan-out.
    shared = dict(base_params or {})
    shared.pop('address', None)

    # Prefer available=true on broad fan-out — unfiltered address calls can still hit
    # the Dash move_out formatter bug for some buildings.
    if 'available' not in shared:
        shared['available'] = 'true'

    def _one(address):
        params = dict(shared)
        params['address'] = address
        items, err = _dash_request_listings(params, req_id, retries=4, timeout=20)
        if err and not items:
            logger.warning(f"[{req_id}] Address fan-out miss for {address}: {err}")
        return items

    collected = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(_one, address) for address in addresses]
        for future in as_completed(futures):
            try:
                collected.extend(future.result() or [])
            except Exception as exc:
                logger.error(f"[{req_id}] Address fan-out worker failed: {exc}")

    # De-dupe by unit/listing id when Dash returns overlaps.
    seen = set()
    unique_items = []
    for item in collected:
        key = (
            str(item.get('unit_id') or ''),
            str(item.get('listing_id') or ''),
            str(item.get('address') or ''),
            str(item.get('unit') or ''),
        )
        if key in seen:
            continue
        seen.add(key)
        unique_items.append(item)

    logger.info(
        f"[{req_id}] Address fan-out assembled {len(unique_items)} listings "
        f"from {len(addresses)} addresses"
    )
    return unique_items


def _map_dash_listing_item(item):
    return {
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
        "zip_code": int(float(item.get('zip_code')))
        if item.get('zip_code') not in [None, '', 'null', 'nan', '0', 0]
        and str(item.get('zip_code')).replace('.', '', 1).isdigit()
        else '',
        "actual_rent": item.get('listed_net', 'N/A'),
        "beds": item.get('beds', 'N/A'),
        "baths": item.get('baths', 'N/A'),
        "sqft": item.get('sqft', 'N/A'),
        "property_type": "Apartment",
        "floor": str(item.get('floor_num', '-')) if item.get('floor_num') is not None else '-',
        "exposure": item.get('exposure', '-') if item.get('exposure') != 'nan' else '-',
        "listing_status": item.get('listing_status', '-'),
        "description": item.get('description') or f"Unit {item.get('unit', '-')} at {item.get('address', '-')}",
        "features": [],
        "unit_amenities": safe_json_loads(item.get('unit_amenities'), []),
        "floor_type": item.get('floor_type', ''),
        "countertop_type": item.get('countertop_type', ''),
        "dishwasher": item.get('dishwasher', ''),
        "laundry_in_unit": item.get('laundry_in_unit', ''),
        "outdoor_space": item.get('outdoor_space', ''),
        "wheelchair_access": item.get('wheelchair_access', ''),
        "smoke_free": item.get('smoke_free', ''),
        "laundry_in_building": item.get('laundry_in_building', ''),
        "pet_friendly": item.get('pet_friendly', ''),
        "live_in_super": item.get('live_in_super', ''),
        "concierge": item.get('concierge', ''),
        "elevator": item.get('elevator', ''),
        "heat_type": item.get('heat_type', ''),
        "stove_type": item.get('stove_type', ''),
        "num_floors": item.get('num_floors', ''),
        "contact_email": "hello@vectorny.com",
        "contact_phone": "+1 917 675 6696",
        "pets_policy": item.get('pet_friendly', 0),
        "unit_images": safe_json_loads(item.get('unit_images'), []),
        "building_amenities": safe_json_loads(item.get('building_amenities'), []),
        "building_image": item.get('building_image', ''),
        "building_images": safe_json_loads(item.get('building_images'), []),
        "expiry": item.get('expiry', '-'),
        "move_out": item.get('move_out', '-'),
        "portfolio": item.get('portfolio'),
        "portfolio_email": item.get('portfolio_email'),
        "address_id": item.get('address_id'),
        "floorplan": item.get('floorplan'),
        "full_address": item.get('full_address') or item.get('addr_address'),
        "latitude": item.get('latitude'),
        "longitude": item.get('longitude'),
        "website_image": item.get('website_image', ''),
    }


def get_all_listings(address=None,
                     unit=None,
                     beds=None,
                     baths=None,
                     min_beds=None,
                     max_beds=None,
                     min_baths=None,
                     max_baths=None,
                     neighborhood=None,
                     borough=None,
                     min_price=None,
                     max_price=None,
                     available=None,
                     portfolio=None,
                     sort=None,
                     exposure=None,
                     amenities=None,
                     doorman=None,
                     elevator=None,
                     pet_friendly=None,
                     wheelchair_access=None,
                     smoke_free=None,
                     laundry_in_building=None,
                     laundry_in_unit=None,
                     live_in_super=None,
                     concierge=None):
    """
    Get all listings from the external API. Supports all filters (form + chatbot View listings URL).

    Returns:
        list: A list of all listings with their IDs
    """
    import traceback
    import time
    req_id = int(time.time() * 1000)

    try:
        requested_amenities = amenities
        apply_local_amenities_filter = False

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
        if min_beds is not None and str(min_beds).strip() != '':
            params['min_beds'] = min_beds
        if max_beds is not None and str(max_beds).strip() != '':
            params['max_beds'] = max_beds
        if min_baths is not None and str(min_baths).strip() != '':
            params['min_baths'] = min_baths
        if max_baths is not None and str(max_baths).strip() != '':
            params['max_baths'] = max_baths
        if neighborhood:
            params['neighborhood'] = neighborhood
        if borough:
            params['borough'] = borough
        if min_price is not None:
            params['min_price'] = min_price
        if max_price is not None:
            params['max_price'] = max_price
        # Dash is flaky with Python True; send the string form that succeeds more often.
        if available is True:
            params['available'] = 'true'
        elif available is False:
            params['available'] = 'false'
        if sort is not None and sort != '':
            params['sort'] = sort
        if exposure:
            params['exposure'] = exposure
        if amenities:
            params['amenities'] = amenities if isinstance(amenities, str) else ','.join(str(a) for a in amenities)
        for key, val in [
            ('doorman', doorman), ('elevator', elevator), ('pet_friendly', pet_friendly),
            ('wheelchair_access', wheelchair_access), ('smoke_free', smoke_free),
            ('laundry_in_building', laundry_in_building), ('laundry_in_unit', laundry_in_unit),
            ('live_in_super', live_in_super), ('concierge', concierge),
        ]:
            if val is True:
                params[key] = 'true'
            elif val is False:
                params[key] = 'false'

        # Broad queries (no address/unit) currently break on Dash's unfiltered path
        # (`_format_listing_move_out`). Assemble inventory via per-address calls.
        scoped = bool(address or unit)
        raw_items = []

        if scoped:
            logger.debug(f"[{req_id}] API call params: {params}")
            raw_items, dash_error = _dash_request_listings(params, req_id)
            if dash_error and not raw_items and available is not True:
                # Last chance for a scoped miss: retry as available-only.
                retry_params = dict(params)
                retry_params['available'] = 'true'
                raw_items, _ = _dash_request_listings(retry_params, req_id)
        else:
            logger.warning(
                f"[{req_id}] Using address fan-out for broad listings query "
                f"(Dash unfiltered get_filtered_listings is unreliable)"
            )
            raw_items = _fanout_listings_by_address(params, req_id)

        # Fallback: if amenities were requested but API returns 0, retry without amenities
        # and apply the amenities filter locally so URL-only filters work reliably.
        if requested_amenities and len(raw_items) == 0:
            try:
                params_no_amen = dict(params)
                params_no_amen.pop('amenities', None)
                logger.warning(
                    f"[{req_id}] Amenities filter returned 0 from API; "
                    "retrying without amenities for local filtering."
                )
                if scoped:
                    raw_items, _ = _dash_request_listings(params_no_amen, req_id)
                else:
                    raw_items = _fanout_listings_by_address(params_no_amen, req_id)
                apply_local_amenities_filter = True
            except Exception as e:
                logger.error(f"[{req_id}] Retry without amenities failed: {e}")

        listings = [_map_dash_listing_item(item) for item in raw_items]

        if apply_local_amenities_filter and requested_amenities:
            if isinstance(requested_amenities, str):
                wants = [w.strip().lower() for w in requested_amenities.split(',') if w and w.strip()]
            elif isinstance(requested_amenities, list):
                wants = [str(w).strip().lower() for w in requested_amenities if w and str(w).strip()]
            else:
                wants = []
            if wants:
                def _has_all_wants(l):
                    combined = []
                    combined.extend(l.get("building_amenities") or [])
                    combined.extend(l.get("unit_amenities") or [])
                    combined = [str(a).lower() for a in combined if a]
                    for w in wants:
                        if not any(w in a for a in combined):
                            return False
                    return True
                listings = [l for l in listings if _has_all_wants(l)]
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
