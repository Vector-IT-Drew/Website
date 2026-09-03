from app import app


SAMPLE_LISTING = {
    'unit_id': '5397',
    'address': '1113 York Ave',
    'unit': '009D',
    'neighborhood': 'Upper East Side',
    'borough': 'Manhattan',
    'zip_code': '10065.0',
    'actual_rent': 6250,
    'beds': 2,
    'baths': 2,
    'sqft': 1100,
    'exposure': 'East',
    'description': 'A bright two-bedroom residence.',
    'unit_amenities': ['Dishwasher'],
    'building_amenities': ['Doorman'],
    'unit_images': ['https://example.com/photo.jpg'],
    'latitude': 40.7595253,
    'longitude': -73.9595718,
    'laundry_in_unit': '1',
    'dishwasher': '1',
    'floorplan': '',
    'contact_phone': '+1 917 675 6696',
}


def test_listing_v2_renders_map_and_keeps_default_intact(monkeypatch):
    monkeypatch.setattr('app.get_listing', lambda listing_id: dict(SAMPLE_LISTING))
    client = app.test_client()

    v2 = client.get('/listings/5397?v=2')
    assert v2.status_code == 200
    html = v2.get_data(as_text=True)
    assert 'vectornyListingMap' in html
    assert 'vectorny_map.js' in html
    assert 'Schedule a Tour' in html
    assert 'Apply Now' in html
    assert '10065' in html
    assert '10065.0' not in html

    default = client.get('/listings/5397')
    assert default.status_code == 200
    default_html = default.get_data(as_text=True)
    assert 'vectornyListingMap' not in default_html
    assert 'osm-map' in default_html or 'property-gallery' in default_html or 'property-title' in default_html
