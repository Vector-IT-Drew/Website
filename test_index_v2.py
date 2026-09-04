from app import app


def test_index_v2_uses_new_homepage_and_default_stays_old():
    client = app.test_client()

    v2 = client.get('/?v=2')
    assert v2.status_code == 200
    html = v2.get_data(as_text=True)
    assert 'v2h-hero' in html
    assert 'Browse Residences' in html
    assert 'vectorny_v2.css' in html
    assert 'Find Your Next Home' in html
    assert 'Investor Services' in html
    assert 'url_for' not in html
    assert '/listings?v=2' in html or 'v=2' in html

    default = client.get('/')
    assert default.status_code == 200
    default_html = default.get_data(as_text=True)
    assert 'v2h-hero' not in default_html
    assert 'hero-section' in default_html
    assert 'Experience the Vector Difference' in default_html
