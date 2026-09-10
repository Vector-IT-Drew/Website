from app import app


def test_about_v2_uses_new_design_and_default_stays_old():
    client = app.test_client()

    v2 = client.get('/about?v=2')
    assert v2.status_code == 200
    html = v2.get_data(as_text=True)
    assert 'vectorny_v2.css' in html
    assert 'v2p-hero' in html
    assert 'Technology Meets Hospitality' in html
    assert '25,000+' in html
    assert 'Browse Listings' in html
    assert 'vectorAssistantModal' in html
    assert '/listings?v=2' in html
    assert 'vectorny_v2.js' in html

    default = client.get('/about')
    assert default.status_code == 200
    default_html = default.get_data(as_text=True)
    assert 'v2p-hero' not in default_html
    assert 'about-hero' in default_html


def test_investor_services_v2_preserves_contact_and_copy():
    client = app.test_client()

    v2 = client.get('/investor-services?v=2')
    assert v2.status_code == 200
    html = v2.get_data(as_text=True)
    assert 'vectorny_v2.css' in html
    assert 'Portfolio Strategy' in html
    assert 'Rent Roll Optimization' in html
    assert 'Challenges of Traditional Leasing' in html
    assert 'contactAgentModal' in html
    assert 'send_hello_email' in html
    assert 'investor.services@vectorny.com' in html
    assert 'Data-Driven Decisions' in html

    default = client.get('/investor-services')
    assert default.status_code == 200
    default_html = default.get_data(as_text=True)
    assert 'v2p-hero' not in default_html
    assert 'service-tile' in default_html


def test_vector_highlights_v2_keeps_galleries_and_portfolio_links():
    client = app.test_client()

    v2 = client.get('/vector-highlights?v=2')
    assert v2.status_code == 200
    html = v2.get_data(as_text=True)
    assert 'vectorny_v2.css' in html
    assert 'Exclusive Portfolio Showcase' in html
    assert 'SMK Greenpoint' in html
    assert 'The Aspen' in html
    assert 'galleryImages' in html
    assert 'galleryImagesAspen' in html
    assert 'portfolio=SMK' in html and 'v=2' in html
    assert 'portfolio=Aspen' in html
    assert 'changeImageAspen' in html

    default = client.get('/vector-highlights')
    assert default.status_code == 200
    default_html = default.get_data(as_text=True)
    assert 'v2hl-portfolio' not in default_html
    assert 'hero-section' in default_html
