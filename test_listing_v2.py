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
    'unit_images': [
        'https://example.com/unit-1.jpg',
        'https://example.com/unit-2.jpg',
        'https://example.com/unit-3.jpg',
    ],
    'building_images': [
        'https://example.com/building-1.jpg',
        'https://example.com/building-2.jpg',
    ],
    'building_image': 'https://example.com/building-1.jpg',
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
    # Fixed navbar clearance + unit photo gallery with broken-url fallback
    assert 'padding: 5.75rem 0 4.5rem' in html
    assert 'v2GalleryPhoto' in html
    assert 'https://example.com/unit-1.jpg' in html
    assert 'data-fallback' in html
    # Gallery walks unit images first, then building images
    assert "data-images='[\"https://example.com/unit-1.jpg\", \"https://example.com/unit-2.jpg\", \"https://example.com/unit-3.jpg\", \"https://example.com/building-1.jpg\", \"https://example.com/building-2.jpg\"]'" in html

    default = client.get('/listings/5397')
    assert default.status_code == 200
    default_html = default.get_data(as_text=True)
    assert 'vectornyListingMap' not in default_html
    assert 'osm-map' in default_html or 'property-gallery' in default_html or 'property-title' in default_html