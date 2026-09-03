"""Helpers for listings preview modal content."""

import re


_BULLET_RE = re.compile(
    r'^(?:[\-\u2010\u2011\u2012\u2013\u2014\u2212\u2022]\s+|\*\s+)(.+)$'
)
_MARKUP_RE = re.compile(r'[*_`]+')


def _clean_text(value):
    if value is None:
        return ''
    text = str(value)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = _MARKUP_RE.sub('', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.strip(' -–—')
    if text.lower() in {'0', '0.0', 'n/a', 'na', 'null', 'none', 'nan', '-'}:
        return ''
    return text


def parse_description_preview(description, max_highlights=4):
    """
    Pull a short summary + highlight bullets from listing markdown/text.
    """
    if not description:
        return '', []

    raw = str(description).replace('\r\n', '\n').replace('\r', '\n')
    lines = [ln.strip() for ln in raw.split('\n') if ln and ln.strip()]

    summary = ''
    highlights = []
    in_building = False

    for line in lines:
        lower = _MARKUP_RE.sub('', line).strip().lower()
        if 'the building' in lower:
            in_building = True
            continue
        if in_building:
            continue

        # Skip section headers like "The Residence:"
        plain = lower.rstrip(':').strip()
        if plain in {'the residence', 'residence', 'unit amenities', 'features'}:
            continue

        bullet = _BULLET_RE.match(line.strip())
        if bullet:
            item = _clean_text(bullet.group(1))
            if item and item not in highlights and len(highlights) < max_highlights:
                highlights.append(item)
            continue

        if not summary:
            candidate = _clean_text(line)
            if candidate and candidate.lower() not in {'the residence', 'residence'}:
                summary = candidate

    if not summary and highlights:
        summary = highlights[0]

    return summary, highlights


def _truthy_flag(value):
    return str(value).strip().lower() in {'true', '1', 'yes', 't', 'y'}


def _has_outdoor(listing):
    if _truthy_flag(listing.get('outdoor_space')):
        return True
    amenities = listing.get('unit_amenities') or []
    joined = ' '.join(str(a).lower() for a in amenities)
    return any(token in joined for token in ('balcony', 'terrace', 'patio', 'outdoor', 'deck'))


def enrich_listing_preview(listing):
    """Attach preview_summary / preview_highlights for the intermediary modal."""
    summary, highlights = parse_description_preview(listing.get('description'))

    fallback_highlights = []
    if _truthy_flag(listing.get('laundry_in_unit')):
        fallback_highlights.append('Full-sized washer & dryer in-unit')
    if _truthy_flag(listing.get('dishwasher')):
        fallback_highlights.append('In-unit dishwasher')
    if _has_outdoor(listing):
        fallback_highlights.append('Private outdoor space')
    if listing.get('floor_type'):
        fallback_highlights.append(f"{listing.get('floor_type')} flooring")
    if listing.get('countertop_type'):
        fallback_highlights.append(f"{listing.get('countertop_type')} countertops")

    for item in fallback_highlights:
        if item not in highlights and len(highlights) < 4:
            highlights.append(item)

    # Do not invent marketing copy when description is blank/placeholder.
    listing['preview_summary'] = summary
    listing['preview_highlights'] = highlights[:4]
    return listing


def format_zip_code(value):
    """Turn API zip values like 10038.0 into a clean 5-digit display zip."""
    if value is None or value is False:
        return ''
    text = str(value).strip()
    if not text or text.lower() in {'0', '0.0', '-', 'n/a', 'na', 'null', 'none', 'nan'}:
        return ''
    try:
        zip_int = int(float(text))
    except (TypeError, ValueError):
        return ''
    if zip_int <= 0:
        return ''
    return f'{zip_int:05d}' if zip_int < 100000 else str(zip_int)


def _has_coords(listing):
    try:
        lat = float(listing.get('latitude'))
        lng = float(listing.get('longitude'))
    except (TypeError, ValueError):
        return False
    return lat != 0 and lng != 0


def ensure_listing_coords(listing):
    """Fill lat/lng from Nominatim when the API leaves them blank."""
    if not listing or _has_coords(listing):
        return listing

    address = listing.get('full_address') or listing.get('address')
    if not address:
        return listing

    query = f"{address}, New York, NY"
    try:
        import requests
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': query, 'format': 'json', 'limit': 1},
            headers={'User-Agent': 'VectorNY-Website/1.0'},
            timeout=6,
        )
        data = response.json() if response.ok else []
        if data:
            listing['latitude'] = float(data[0]['lat'])
            listing['longitude'] = float(data[0]['lon'])
    except Exception:
        pass
    return listing
