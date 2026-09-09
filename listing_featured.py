"""Homepage featured-listing helpers for v=2."""

from database import get_all_listings


# Portfolios highlighted on Vector Highlights / marketing surfaces.
FEATURED_PORTFOLIOS = ('SMK', 'Aspen')


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
    listing['featured_image'] = images[0] if images else '/static/images/listing-coming-soon.jpg'
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

    1) Pull known featured portfolios (e.g. SMK / Aspen)
    2) Prefer units with photos
    3) Fill from the default listings feed (API featured/default order)
    """
    limit = max(1, int(limit or 8))
    featured = []
    for portfolio in FEATURED_PORTFOLIOS:
        try:
            featured.extend(get_all_listings(portfolio=portfolio) or [])
        except Exception:
            continue

    try:
        general = get_all_listings() or []
    except Exception:
        general = []

    # Prefer photo-rich featured units, then any featured, then photo-rich general, then rest.
    featured_photos = [l for l in featured if _has_photo(l)]
    featured_rest = [l for l in featured if not _has_photo(l)]
    general_photos = [l for l in general if _has_photo(l)]
    general_rest = [l for l in general if not _has_photo(l)]

    return _merge_unique(
        featured_photos + featured_rest + general_photos,
        general_rest,
        limit,
    )
