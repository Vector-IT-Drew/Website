"""Homepage featured-listing helpers for v=2."""

from database import get_all_listings


# Portfolios highlighted on Vector Highlights / marketing surfaces.
FEATURED_PORTFOLIOS = ('SMK', 'Aspen')

COMING_SOON_IMAGES = (
    'https://dl.dropboxusercontent.com/scl/fi/fy2wl340lre6y2gm84m13/img-coming-soon-2.jpeg'
    '?rlkey=xkao9jz2p6mrznqhb8e3hf7w6&st=k3gwz5kj&dl=0',
    'https://dl.dropboxusercontent.com/scl/fi/5kqjpn1lqdt6p73zo5xkj/img-coming-soon-3.jpeg'
    '?rlkey=ngk4iu9pvl6jusqps220pi2uv&st=ttncu3xt&dl=0',
    'https://dl.dropboxusercontent.com/scl/fi/in5oflurzeui3k61z2vh6/img-coming-soon-4.jpeg'
    '?rlkey=rp9ucjxfih59yldqgsib9ukdl&st=4byf8tgo&dl=0',
    'https://dl.dropboxusercontent.com/scl/fi/erhz52z0z7lskr8ru5v1h/img-coming-soon-5.jpeg'
    '?rlkey=bf8j1tpvtqb2q02tcjy0mdp3v&st=r7mtn0d7&dl=0',
)


def _coming_soon_for(listing):
    unit_id = str(listing.get('unit_id') or listing.get('id') or '0')
    try:
        idx = abs(hash(unit_id)) % len(COMING_SOON_IMAGES)
    except Exception:
        idx = 0
    return COMING_SOON_IMAGES[idx]


def _clean_image_url(raw):
    url = str(raw or '').strip()
    if not url:
        return ''
    if url.lower() in {'0', '0.0', 'n/a', 'na', '-', 'null', 'none'}:
        return ''
    return url


def _listing_images(listing):
    images = []
    seen = set()

    # Prefer marketing/website hero image when present.
    website = _clean_image_url(listing.get('website_image'))
    if website and website not in seen:
        seen.add(website)
        images.append(website)

    for raw in (listing.get('unit_images') or []):
        url = _clean_image_url(raw)
        if not url or url in seen:
            continue
        seen.add(url)
        images.append(url)

    building = _clean_image_url(listing.get('building_image'))
    if building and building not in seen:
        images.append(building)
    return images


def _has_photo(listing):
    return bool(_listing_images(listing))


def _normalize_listing(listing):
    listing = dict(listing or {})
    images = _listing_images(listing)
    listing['unit_images'] = images
    listing['featured_image'] = images[0] if images else _coming_soon_for(listing)
    listing['is_featured_portfolio'] = str(listing.get('portfolio') or '').strip().lower() in {
        p.lower() for p in FEATURED_PORTFOLIOS
    }
    return listing


def _merge_unique(primary, secondary, limit):
    chosen = []
    seen = set()
    for source in (primary, secondary):
        for listing in source:
            unit_id = str(listing.get('unit_id') or listing.get('id') or '')
            if not unit_id or unit_id in seen:
                continue
            seen.add(unit_id)
            chosen.append(_normalize_listing(listing))
            if len(chosen) >= limit:
                return chosen
    return chosen


def get_homepage_featured_listings(limit=8):
    """
    Featured-first homepage strip.

    Uses a single listings API call (faster than per-portfolio fetches),
    then prefers known featured portfolios and photo-rich units.
    """
    limit = max(1, int(limit or 8))
    try:
        general = get_all_listings() or []
    except Exception:
        general = []

    featured_names = {p.lower() for p in FEATURED_PORTFOLIOS}
    featured = [
        l for l in general
        if str(l.get('portfolio') or '').strip().lower() in featured_names
    ]
    # Units already counted as featured should not be duplicated from general fill.
    featured_ids = {
        str(l.get('unit_id') or l.get('id') or '')
        for l in featured
    }
    rest = [
        l for l in general
        if str(l.get('unit_id') or l.get('id') or '') not in featured_ids
    ]

    featured_photos = [l for l in featured if _has_photo(l)]
    featured_rest = [l for l in featured if not _has_photo(l)]
    general_photos = [l for l in rest if _has_photo(l)]
    general_rest = [l for l in rest if not _has_photo(l)]

    return _merge_unique(
        featured_photos + featured_rest + general_photos,
        general_rest,
        limit,
    )
