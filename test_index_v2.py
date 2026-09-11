from app import app


def test_index_v2_uses_new_homepage_and_default_stays_old(monkeypatch):
    monkeypatch.setattr('app.get_all_listings', lambda **kwargs: [])
    monkeypatch.setattr(
        'app.get_homepage_featured_content',
        lambda listings=None, listing_limit=8, dash_host=None: (
            [{
                'unit_id': '5551',
                'address': '1113 York Avenue',
                'unit': '036B',
                'building_name': 'York House',
                'neighborhood': 'Upper East Side',
                'actual_rent': 9500,
                'beds': 2,
                'baths': 2,
                'featured_image': 'https://example.com/photo.jpg',
                'is_featured_portfolio': True,
            }],
            [{
                'address_id': 506,
                'address': '1955 1st Avenue',
                'building_name': '',
                'portfolio': 'The Aspen',
                'neighborhood': 'Upper East Side',
                'images': ['https://example.com/building.jpg'],
                'amenities': ['Gym', 'Pool', 'Sky Lounge'],
                'available_units': 12,
                'price_from': 4200,
                'bedrooms_label': 'Studio - 2 Bed',
                'schedule_tour_url': 'https://example.com/tour',
                'listings_url': '/listings?v=2&address=1955%201st%20Avenue&portfolio=The%20Aspen',
            }],
        ),
    )
    client = app.test_client()

    v2 = client.get('/?v=2')
    assert v2.status_code == 200
    html = v2.get_data(as_text=True)
    assert 'v2h-hero' in html
    assert '100vh' in html
    assert 'marbleskyline-darknavy.webp' in html
    assert 'v2h-hero-bg' in html
    assert 'height: 136%' in html
    assert 'coming-soon' in html
    assert 'rel="preload"' in html
    assert 'Leasing Simplified' in html
    assert 'Browse Residences' in html
    assert 'vectorny_v2.css' in html
    assert 'Find Your Next Home' in html
    assert 'Investor Services' in html
    assert 'v2h-featured' in html
    assert 'Featured Residences' in html
    assert '/listings/5551?v=2' in html
    assert 'York House' in html
    assert 'Featured Buildings' in html
    assert '1955 1st Avenue' in html
    assert 'v2h-building-card' in html
    assert 'v2h-building-summary' in html
    assert 'buildingPreviewOverlay' in html
    assert 'Building amenities' in html
    assert 'Sky Lounge' in html
    assert '12 available' in html
    assert 'Studio - 2 Bed' in html
    assert 'From $4,200' in html
    assert 'v2h-building-chip' not in html
    assert 'v2h-building-amenities-label' not in html
    assert 'grid-template-columns: 1.05fr' not in html
    assert 'aspect-ratio: 16 / 10' in html

    default = client.get('/')
    assert default.status_code == 200
    default_html = default.get_data(as_text=True)
    assert 'v2h-hero' not in default_html
    assert 'hero-section' in default_html
    assert 'Experience the Vector Difference' in default_html
