from app import app


SAMPLE_LISTINGS = [
    {
        'unit_id': '5551',
        'address': '1113 York Avenue',
        'unit': '036B',
        'building_name': 'York House',
        'neighborhood': 'Upper East Side',
        'borough': 'Manhattan',
        'actual_rent': 9500,
        'beds': 2,
        'baths': 2,
        'sqft': 1100,
        'exposure': 'East',
        'unit_images': ['https://example.com/a.jpg'],
        'building_image': '',
        'move_out': '',
        'laundry_in_unit': '1',
        'dishwasher': '1',
        'outdoor_space': '0',
        'unit_amenities': [],
        'preview_summary': 'Bright residence',
        'preview_highlights': ['Washer dryer'],
    },
    {
        'unit_id': '5552',
        'address': '525 East 72nd Street',
        'unit': '12A',
        'building_name': '1 East River Place',
        'neighborhood': 'Upper East Side',
        'borough': 'Manhattan',
        'actual_rent': 8850,
        'beds': 2,
        'baths': 2,
        'sqft': 1000,
        'exposure': 'South',
        'unit_images': [],
        'building_image': '',
        'move_out': '04/01/2026',
        'laundry_in_unit': '0',
        'dishwasher': '0',
        'outdoor_space': '1',
        'unit_amenities': ['Balcony'],
        'preview_summary': '',
        'preview_highlights': [],
    },
]


def test_listings_v2_uses_new_grid_and_default_stays_old(monkeypatch):
    monkeypatch.setattr('app.get_all_listings', lambda **kwargs: [dict(x) for x in SAMPLE_LISTINGS])
    monkeypatch.setattr('app.requests.get', lambda *args, **kwargs: type('R', (), {
        'json': staticmethod(lambda: {'unique_neighborhoods': ['Upper East Side'], 'unique_addresses': ['1113 York Avenue']}),
        'raise_for_status': staticmethod(lambda: None),
    })())

    client = app.test_client()
    v2 = client.get('/listings?v=2')
    assert v2.status_code == 200
    html = v2.get_data(as_text=True)
    assert 'v2l-grid' in html
    assert 'v2l-card' in html
    assert 'Available Now' in html
    assert 'Available on 04/01/2026' in html
    assert 'Find Residences' in html
    assert 'repeat(3, minmax(0, 1fr))' in html
    assert 'listing-card h-100' not in html
    assert 'v2l-amenity' in html
    assert 'In-Unit Laundry' in html
    assert 'Dishwasher' in html
    assert 'Outdoor Space' in html
    assert 'Sq Ft' in html
    assert 'v2l-amenities' in html
    assert html.index('class="v2l-amenities"') < html.index('class="v2l-badge"')
    assert html.index('class="v2l-amenities"') < html.index('class="v2l-body"')

    default = client.get('/listings')
    assert default.status_code == 200
    default_html = default.get_data(as_text=True)
    assert 'v2l-grid' not in default_html
    assert 'listing-card' in default_html
