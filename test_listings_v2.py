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
        'exposure': 'SW',
        'unit_images': [],
        'building_image': 'https://example.com/BUILDING-ONLY.jpg',
        'move_out': '04/01/2026',
        'laundry_in_unit': '0',
        'dishwasher': '0',
        'outdoor_space': '1',
        'unit_amenities': ['Balcony'],
        'preview_summary': '',
        'preview_highlights': [],
    },
    {
        'unit_id': '5553',
        'address': '200 East 61st Street',
        'unit': '8C',
        'building_name': 'Sutton Tower',
        'neighborhood': 'Midtown East',
        'borough': 'Manhattan',
        'actual_rent': 4200,
        'beds': 0,
        'baths': 1,
        'sqft': 500,
        'exposure': '',
        'unit_images': ['https://example.com/c.jpg'],
        'building_image': '',
        'move_out': '',
        'laundry_in_unit': '0',
        'dishwasher': '0',
        'outdoor_space': '0',
        'unit_amenities': [],
        'preview_summary': '',
        'preview_highlights': [],
    },
]


def test_exposure_dirs_filter():
    from app import exposure_dirs
    assert exposure_dirs('East') == ['E']
    assert exposure_dirs('SW') == ['S', 'W']
    assert exposure_dirs('South-West') == ['S', 'W']
    assert exposure_dirs('N/E') == ['N', 'E']
    assert exposure_dirs('') == []
    assert exposure_dirs('-') == []
    assert exposure_dirs(None) == []


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
    assert 'gap: 1.35rem' in html
    assert 'v2l-photo' in html
    assert 'loading=' in html
    assert 'img-coming-soon' in html
    assert 'BUILDING-ONLY.jpg' not in html
    assert 'listing-card h-100' not in html
    assert 'v2l-amenity' in html
    assert 'In-Unit Laundry' in html
    assert 'Dishwasher' in html
    assert 'Outdoor Space' in html
    assert 'Sq Ft' in html
    assert 'v2l-amenities' in html
    assert html.index('class="v2l-amenities"') < html.index('class="v2l-badge"')
    assert html.index('class="v2l-amenities"') < html.index('class="v2l-body"')
    # Exposure compass on photos: East → E; SW → S+W; empty → hidden
    assert 'v2l-exposure' in html
    assert 'v2l-exposure-dir is-on">E<' in html
    assert 'v2l-exposure-dir is-on">S<' in html
    assert 'v2l-exposure-dir is-on">W<' in html
    assert html.count('class="v2l-exposure"') == 2
    assert 'v2l-exposure-dot' in html
    assert 'aria-label="Exposure East"' in html
    assert 'aria-label="Exposure SW"' in html
    assert 'max-width: calc(100% - 5.75rem)' in html
    assert 'background: transparent' in html
    assert 'width: min(1180px, 100%)' in html
    assert 'minmax(0, 1.38fr)' in html

    default = client.get('/listings')
    assert default.status_code == 200
    default_html = default.get_data(as_text=True)
    assert 'v2l-grid' not in default_html
    assert 'listing-card' in default_html
