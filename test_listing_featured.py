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

    assert [item['unit_id'] for item in featured] == ['2', '3']
    assert all(item['is_featured_portfolio'] is True for item in featured)
    assert featured[0]['featured_image'] == 'https://example.com/web.jpg'


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
            'amenities': [],
            'available_units': 0,
            'price_from': None,
            'bedrooms_label': '',
            'schedule_tour_url': 'https://example.com/tour',
            'listings_url': '/listings?v=2&address=1955%201st%20Avenue&portfolio=The%20Aspen',
        }],
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
