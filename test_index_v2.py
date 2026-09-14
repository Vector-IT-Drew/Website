from app import app


def _featured_building(**overrides):
    building = {
        'address_id': 506,
        'address': '1955 1st Avenue',
        'building_name': '',
        'portfolio': 'The Aspen',
        'neighborhood': 'Upper East Side',
        'images': [
            'https://example.com/building.jpg',
            'https://example.com/building-2.jpg',
            'https://example.com/building-3.jpg',
        ],
        'amenities': ['Gym', 'Pool', 'Sky Lounge'],
        'available_units': 12,
        'price_from': 4200,
        'bedrooms_label': 'Studio - 2 Bed',
        'schedule_tour_url': 'https://example.com/tour',
        'listings_url': '/listings?v=2&address=1955%201st%20Avenue&portfolio=The%20Aspen',
    }
    building.update(overrides)
    return building


def _featured_listing(**overrides):
    listing = {
        'unit_id': '5551',
        'address': '1113 York Avenue',
        'unit': '036B',
        'building_name': 'York House',
        'neighborhood': 'Upper East Side',
        'actual_rent': 9500,
        'beds': 2,
        'baths': 2,
        'featured_image': 'https://example.com/photo.jpg',
        'unit_images': [
            'https://example.com/photo.jpg',
            'https://example.com/photo-2.jpg',
        ],
        'is_featured_portfolio': True,
    }
    listing.update(overrides)
    return listing


def test_index_v2_uses_new_homepage_and_default_stays_old(monkeypatch):
    monkeypatch.setattr(
        'app.fetch_featured_portfolio_buildings',
        lambda **kwargs: [_featured_building()],
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
    assert 'A curated selection of homes from our featured buildings across the city.' in html
    assert 'inventory database' not in html
    assert 'Featured Buildings' in html
    assert '1955 1st Avenue' in html
    assert 'v2h-building-card' in html
    assert 'v2h-building-summary' in html
    assert 'v2h-building-address' in html
    assert 'v2h-buildings-nav' in html
    assert 'v2h-building-shot' in html
    assert 'has-gallery' in html
    assert 'featuredBuildingsTrack' in html
    assert 'buildingPreviewOverlay' in html
    assert 'Building amenities' in html
    assert 'Sky Lounge' in html
    assert '12 available' in html
    assert 'Studio - 2 Bed' in html
    assert 'From $4,200' in html
    assert 'translateY(calc(-20vh + 50px))' in html
    assert 'margin-top: clamp(4.75rem, 11vh, 7.5rem)' in html
    assert 'bindHeroSkylineFade' in html
    assert 'data-async="1"' in html
    assert 'api/homepage-featured' in html
    assert 'src="https://example.com/building.jpg"' in html
    assert 'src="[' not in html
    assert 'v2h-building-chip' not in html
    assert 'v2h-building-amenities-label' not in html
    assert 'v2h-building-badge' not in html
    assert '>Featured<' not in html
    assert 'availability_label' in html
    assert 'Available Now' in html
    assert 'v2h-featured-unit' in html
    assert 'aspect-ratio: 16 / 10' in html
    # Building preview: larger modal, wider copy column, side-by-side CTAs, no layout wrap
    assert 'width: min(1120px, 100%)' in html
    assert 'grid-template-columns: 1.05fr 0.95fr' in html
    assert 'white-space: nowrap' in html
    assert 'grid-template-columns: 1fr 1fr' in html
    assert 'align-content: flex-start' in html
    assert 'flex: 0 1 auto' in html
    assert 'is-crossfading' in html
    assert 'is-swap-out' in html
    assert 'preloadImage' in html
    assert 'v2hFeaturedImgError' in html
    assert 'collapseFeaturedMediaToFallback' in html
    assert 'v2h-featured-media-link' in html
    assert 'stopImmediatePropagation' in html
    assert '<article class="v2h-featured-card">' in html
    assert 'buildingPreviewListings' in html
    assert 'buildingPreviewTour' in html
    assert 'v2h-featured-shot' in html

    default = client.get('/')
    assert default.status_code == 200
    default_html = default.get_data(as_text=True)
    assert 'v2h-hero' not in default_html
    assert 'hero-section' in default_html
    assert 'Experience the Vector Difference' in default_html


def test_homepage_featured_api_returns_listings_and_buildings(monkeypatch):
    monkeypatch.setattr(
        'app.get_homepage_featured_content',
        lambda listings=None, listing_limit=8, dash_host=None: (
            [_featured_listing()],
            [_featured_building()],
        ),
    )
    client = app.test_client()
    response = client.get('/api/homepage-featured')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['featured_listings'][0]['unit_id'] == '5551'
    assert payload['featured_buildings'][0]['address'] == '1955 1st Avenue'
