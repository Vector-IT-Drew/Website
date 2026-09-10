from app import app


def test_index_v2_uses_new_homepage_and_default_stays_old(monkeypatch):
    monkeypatch.setattr(
        'app.get_homepage_featured_listings',
        lambda limit=8: [{
            'unit_id': '5551',
            'address': '1113 York Avenue',
            'unit': '036B',
            'building_name': 'York House',
            'neighborhood': 'Upper East Side',
            'actual_rent': 9500,
            'beds': 2,
            'baths': 2,
            'featured_image': 'https://example.com/photo.jpg',
            'is_featured_portfolio': False,
        }],
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
    assert 'img-coming-soon' in html
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

    default = client.get('/')
    assert default.status_code == 200
    default_html = default.get_data(as_text=True)
    assert 'v2h-hero' not in default_html
    assert 'hero-section' in default_html
    assert 'Experience the Vector Difference' in default_html
