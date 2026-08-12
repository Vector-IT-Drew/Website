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

    if not summary:
        beds = listing.get('beds')
        if beds == 0 or str(beds) == '0':
            bed_label = 'Studio'
        else:
            try:
                bed_num = float(beds)
                bed_label = '1 Bedroom' if bed_num == 1 else f'{bed_num:g} Bedrooms'
            except (TypeError, ValueError):
                bed_label = 'Residence'

        hood = listing.get('neighborhood')
        if hood in (None, '', '-', '0'):
            hood = 'New York'
        summary = f'{bed_label} in {hood}.'

    listing['preview_summary'] = summary
    listing['preview_highlights'] = highlights[:4]
    return listing
