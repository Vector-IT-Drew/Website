"""Homepage featured content must use portfolios.is_featured only."""

from listing_featured import select_featured_listings, get_homepage_featured_content


def _listing(**kwargs):
    base = {
        'unit_id': '1',
        'address': '1 Test Ave',
        'unit': '1A',
        'building_name': 'Test House',
        'neighborhood': 'UES',
        'portfolio': 'Other',
        'actual_rent': 5000,
        'beds': 1,
        'baths': 1,
        'unit_images': ['https://example.com/a.jpg'],
        'website_image': '',
        'building_image': '',
        'address_id': 1,
    }
    base.update(kwargs)
    return base


def test_select_featured_listings_uses_only_is_featured_portfolios():
    featured = select_featured_listings(
        [
            _listing(unit_id='1', portfolio='525', address='1 Test Ave'),
            _listing(
                unit_id='2',
                portfolio='The Aspen',
                address='1955 1st Avenue',
                address_id=506,
                unit_images=[],
                website_image='https://example.com/web.jpg',
            ),
            _listing(
                unit_id='3',
                portfolio='Other',
                address='68-64 Yellowstone Boulevard',
                address_id=591,
                unit_images=['https://example.com/y.jpg'],
            ),
        ],
        limit=8,
        featured_portfolio_names=['The Aspen', 'Yellowstone'],
        featured_buildings=[
            {'address_id': 506, 'address': '1955 1st Avenue', 'portfolio': 'The Aspen'},
            {'address_id': 591, 'address': '68-64 Yellowstone Boulevard', 'portfolio': 'Yellowstone'},
        ],
    )

    assert [item['unit_id'] for item in featured] == ['3', '2']
    assert all(item['is_featured_portfolio'] is True for item in featured)
    # Unit with unit_images is preferred over website-only fallback.
    assert featured[0]['featured_image'] == 'https://example.com/y.jpg'
    assert featured[1]['featured_image'] == 'https://example.com/web.jpg'
    assert featured[0]['availability_label'] == 'Available Now'


def test_select_featured_listings_respects_limit_of_ten():
    rows = [
        _listing(
            unit_id=str(i),
            portfolio='The Aspen',
            address='1955 1st Avenue',
            address_id=506,
            unit_images=[f'https://example.com/{i}.jpg'],
        )
        for i in range(1, 25)
    ]
    featured = select_featured_listings(
        rows,
        limit=10,
        featured_portfolio_names=['The Aspen'],
        featured_buildings=[
            {'address_id': 506, 'address': '1955 1st Avenue', 'portfolio': 'The Aspen'},
        ],
    )
    assert len(featured) == 10
    assert all(item['featured_image'].startswith('https://example.com/') for item in featured)


def test_select_featured_listings_does_not_fill_from_other_inventory():
    featured = select_featured_listings(
        [
            _listing(unit_id='1', portfolio='525', address='1 Test Ave'),
            _listing(unit_id='2', portfolio='SMK', address='5 Sutton St'),
        ],
        limit=8,
        featured_portfolio_names=['The Aspen'],
        featured_buildings=[
            {'address_id': 506, 'address': '1955 1st Avenue', 'portfolio': 'The Aspen'},
        ],
    )
    assert featured == []


def test_get_homepage_featured_content_enriches_buildings(monkeypatch):
    monkeypatch.setattr(
        'listing_featured.fetch_featured_portfolio_names',
        lambda connection=None: ['The Aspen'],
    )
    monkeypatch.setattr(
        'listing_featured.fetch_featured_portfolio_buildings',
        lambda connection=None, dash_host=None: [{
            'address_id': 506,
            'address': '1955 1st Avenue',
            'neighborhood': '',
            'building_name': '',
            'portfolio': 'The Aspen',
            'portfolio_id': 37,
            'entity_id': '187.0',
            'entity_name': 'ASPEN 2016 LLC',
            'images': ['https://example.com/soon.png'],
            'amenities': ['Gym', 'Pool'],
            'available_units': 0,
            'price_from': None,
            'bedrooms_label': '',
            'schedule_tour_url': 'https://example.com/tour',
            'listings_url': '/listings?v=2&address=1955%201st%20Avenue&portfolio=The%20Aspen',
        }],
    )
    monkeypatch.setattr(
        'listing_featured.fetch_listings_for_buildings',
        lambda buildings: [],
    )

    featured_listings, featured_buildings = get_homepage_featured_content(
        [
            _listing(
                unit_id='2',
                portfolio='The Aspen',
                address='1955 1st Avenue',
                address_id=506,
                actual_rent=4200,
                beds=2,
                unit_images=['https://example.com/unit.jpg'],
            )
        ],
        listing_limit=8,
        dash_host='https://example.com',
    )
    assert len(featured_listings) == 1
    assert featured_buildings[0]['available_units'] == 1
    assert featured_buildings[0]['price_from'] == 4200.0
    assert featured_buildings[0]['bedrooms_label'] == '2 Bed'
    assert featured_buildings[0]['amenities'] == ['Gym', 'Pool']


def test_fetch_listings_for_buildings_queries_by_address(monkeypatch):
    calls = []

    def fake_get_all_listings(**kwargs):
        calls.append(kwargs)
        if kwargs.get('address') == '420 East 61st Street':
            return [_listing(
                unit_id='9',
                address='420 East 61st Street',
                address_id=534,
                portfolio='1 Sutton',
                actual_rent=4100,
                beds=1,
            )]
        return []

    monkeypatch.setattr('database.get_all_listings', fake_get_all_listings)
    rows = __import__('listing_featured', fromlist=['fetch_listings_for_buildings']).fetch_listings_for_buildings([
        {'address': '420 East 61st Street', 'address_id': 534},
        {'address': '1955 1st Avenue', 'address_id': 506},
    ])
    assert len(rows) == 1
    assert rows[0]['unit_id'] == '9'
    assert {c['address'] for c in calls} == {'420 East 61st Street', '1955 1st Avenue'}
    assert all(c['available'] is True for c in calls)


def test_enrich_buildings_uses_compact_bedroom_range():
    from listing_featured import _enrich_buildings_from_listings
    buildings = [{
        'address_id': 1,
        'address': '1 Test Ave',
        'images': ['https://example.com/a.jpg'],
        'amenities': ['Gym'],
    }]
    listings = [
        {'address_id': 1, 'address': '1 Test Ave', 'beds': 0, 'actual_rent': 3000, 'unit_images': []},
        {'address_id': 1, 'address': '1 Test Ave', 'beds': 1, 'actual_rent': 3500, 'unit_images': []},
        {'address_id': 1, 'address': '1 Test Ave', 'beds': 3, 'actual_rent': 5000, 'unit_images': []},
    ]
    enriched = _enrich_buildings_from_listings(buildings, listings)
    assert enriched[0]['bedrooms_label'] == 'Studio - 3 Bed'
    assert enriched[0]['available_units'] == 3
    assert enriched[0]['price_from'] == 3000.0
    # Building cards keep address-level images only (no unit photo bleed-in).
    assert enriched[0]['images'] == ['https://example.com/a.jpg']


def test_listing_images_ignore_building_photos():
    from listing_featured import _listing_images
    images = _listing_images({
        'unit_images': [],
        'website_image': '',
        'building_image': 'https://example.com/building.jpg',
        'building_images': ['https://example.com/building-2.jpg'],
    })
    assert images == []


def test_availability_label_matches_listings():
    from listing_featured import _availability_label
    assert _availability_label({'move_out': ''}) == 'Available Now'
    assert _availability_label({'move_out': '09/09/1999'}) == 'Available Now'
    assert _availability_label({'move_out': '10/01/2026'}) == 'Available on 10/01/2026'


def test_parse_image_list_handles_json_list_strings():
    from listing_featured import _parse_image_list
    assert _parse_image_list('["https://example.com/a.jpg"]') == ['https://example.com/a.jpg']
    assert _parse_image_list('[https://example.com/a.jpg]') == ['https://example.com/a.jpg']
    assert _parse_image_list(
        '[https://example.com/a.jpg, https://example.com/b.jpg, https://example.com/c.jpg]'
    ) == [
        'https://example.com/a.jpg',
        'https://example.com/b.jpg',
        'https://example.com/c.jpg',
    ]
    assert _parse_image_list(
        '["https://example.com/a.jpg", "https://example.com/b.jpg"]'
    ) == [
        'https://example.com/a.jpg',
        'https://example.com/b.jpg',
    ]
    assert _parse_image_list(
        "['https://example.com/a.jpg', 'https://example.com/b.jpg']"
    ) == [
        'https://example.com/a.jpg',
        'https://example.com/b.jpg',
    ]
    assert _parse_image_list(['https://example.com/a.jpg', 'https://example.com/b.jpg']) == [
        'https://example.com/a.jpg',
        'https://example.com/b.jpg',
    ]
    assert _parse_image_list('https://example.com/a.jpg') == ['https://example.com/a.jpg']
