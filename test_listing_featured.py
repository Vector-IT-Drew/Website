from listing_featured import get_homepage_featured_listings


def test_homepage_featured_fills_from_general_when_portfolio_empty(monkeypatch):
    sample = [
        {
            'unit_id': '1',
            'address': '1 Test Ave',
            'unit': '1A',
            'building_name': 'Test House',
            'neighborhood': 'UES',
            'portfolio': '525',
            'actual_rent': 5000,
            'beds': 1,
            'baths': 1,
            'unit_images': ['https://example.com/a.jpg'],
            'building_image': '',
        },
        {
            'unit_id': '2',
            'address': '2 Test Ave',
            'unit': '2B',
            'building_name': '-',
            'neighborhood': 'Midtown',
            'portfolio': 'Other',
            'actual_rent': 4200,
            'beds': 0,
            'baths': 1,
            'unit_images': [],
            'building_image': '',
        },
    ]

    def fake_get_all_listings(portfolio=None, **kwargs):
        if portfolio:
            return []
        return [dict(x) for x in sample]

    monkeypatch.setattr('listing_featured.get_all_listings', fake_get_all_listings)
    featured = get_homepage_featured_listings(limit=8)
    assert len(featured) == 2
    assert featured[0]['unit_id'] == '1'
    assert featured[0]['featured_image'].startswith('https://example.com/a.jpg')
    assert featured[0]['is_featured_portfolio'] is False


def test_homepage_featured_prefers_named_portfolios(monkeypatch):
    def fake_get_all_listings(portfolio=None, **kwargs):
        if portfolio == 'SMK':
            return [{
                'unit_id': '99',
                'address': '5 Sutton St',
                'unit': 'PH',
                'building_name': 'SMK Home',
                'neighborhood': 'Greenpoint',
                'portfolio': 'SMK',
                'actual_rent': 3900,
                'beds': 2,
                'baths': 1,
                'unit_images': ['https://example.com/smk.jpg'],
                'building_image': '',
            }]
        if portfolio:
            return []
        return [{
            'unit_id': '1',
            'address': '1 Test Ave',
            'unit': '1A',
            'building_name': 'Test House',
            'neighborhood': 'UES',
            'portfolio': '525',
            'actual_rent': 5000,
            'beds': 1,
            'baths': 1,
            'unit_images': ['https://example.com/a.jpg'],
            'building_image': '',
        }]

    monkeypatch.setattr('listing_featured.get_all_listings', fake_get_all_listings)
    featured = get_homepage_featured_listings(limit=8)
    assert featured[0]['unit_id'] == '99'
    assert featured[0]['is_featured_portfolio'] is True
    assert featured[1]['unit_id'] == '1'
