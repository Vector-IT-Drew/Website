from listing_preview import (
    enrich_listing_preview,
    ensure_listing_coords,
    format_zip_code,
    parse_description_preview,
)


def test_parse_description_preview_extracts_summary_and_bullets():
    description = """*Large three-bedroom residence with river views*

 *The Residence:*

 - Full-sized washer and dryer in-unit

 - Floor-to-ceiling windows with East River views

 - Rich wood cabinetry with sleek marble countertops

 *The Building:*

 - Pool and gym
"""
    summary, highlights = parse_description_preview(description)
    assert 'three-bedroom' in summary.lower()
    assert any('washer' in h.lower() for h in highlights)
    assert all('pool' not in h.lower() for h in highlights)


def test_enrich_listing_preview_falls_back_to_unit_flags():
    listing = {
        'description': '',
        'beds': 1,
        'neighborhood': 'Upper East Side',
        'laundry_in_unit': '1',
        'dishwasher': '1',
        'outdoor_space': '0',
        'unit_amenities': [],
    }
    enrich_listing_preview(listing)
    assert listing['preview_summary'] == ''
    assert any('washer' in h.lower() for h in listing['preview_highlights'])
    assert any('dishwasher' in h.lower() for h in listing['preview_highlights'])


def test_format_zip_code_strips_decimal():
    assert format_zip_code('10038.0') == '10038'
    assert format_zip_code(10022) == '10022'
    assert format_zip_code(None) == ''
    assert format_zip_code('0') == ''


def test_ensure_listing_coords_keeps_existing_values():
    listing = {'address': '1 Sutton Place', 'latitude': 40.7571553, 'longitude': -73.9601282}
    assert ensure_listing_coords(listing)['latitude'] == 40.7571553
