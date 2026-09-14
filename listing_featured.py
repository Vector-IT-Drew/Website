"""Homepage featured listings and buildings from portfolios.is_featured only."""

from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import quote

import mysql.connector

from tour_schedule import build_tour_schedule_url

COMING_SOON_IMAGES = [
    (
        "https://dl.dropboxusercontent.com/scl/fi/fy2wl340lre6y2gm84m13/img-coming-soon-2.jpeg"
        "?rlkey=xkao9jz2p6mrznqhb8e3hf7w6&st=k3gwz5kj&dl=0"
    ),
    (
        "https://dl.dropboxusercontent.com/scl/fi/5kqjpn1lqdt6p73zo5xkj/img-coming-soon-3.jpeg"
        "?rlkey=ngk4iu9pvl6jusqps220pi2uv&st=ttncu3xt&dl=0"
    ),
    (
        "https://dl.dropboxusercontent.com/scl/fi/in5oflurzeui3k61z2vh6/img-coming-soon-4.jpeg"
        "?rlkey=rp9ucjxfih59yldqgsib9ukdl&st=x5td7577&dl=0"
    ),
    (
        "https://dl.dropboxusercontent.com/scl/fi/erhz52z0z7lskr8ru5v1h/img-coming-soon-5.jpeg"
        "?rlkey=bf8j1tpvtqb2q02tcjy0mdp3v&st=r7mtn0d7&dl=0"
    ),
]

# Same defaults as Vector Database connect_MYSQL.py
_DEFAULT_DB_HOST = "35.231.226.236"
_DEFAULT_DB_USER = "vector-dash-user"
_DEFAULT_DB_PASSWORD = "VectorIT104!"
_DEFAULT_DB_NAME = "dash-database"
_DEFAULT_DASH_HOST = "https://dash-production-b25c.up.railway.app"


def _coming_soon_image_for(seed: Any) -> str:
    text = str(seed or "").strip() or "coming-soon"
    return COMING_SOON_IMAGES[sum(ord(ch) for ch in text) % len(COMING_SOON_IMAGES)]


def _normalize_portfolio_name(value: Any) -> str:
    text = " ".join(str(value or "").strip().lower().split())
    if text.startswith("the "):
        text = text[4:].strip()
    return text


def _clean_text(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if text.lower() in {"0", "0.0", "n/a", "na", "-", "null", "none", "nan"}:
        return ""
    return text


def _first_non_empty(*values: Any) -> str:
    for value in values:
        text = _clean_text(value)
        if text:
            return text
    return ""


def _clean_image_url(raw: Any) -> str:
    url = _clean_text(raw)
    if not url or url.lower() in {"0", "0.0"}:
        return ""
    # Reject JSON / list blobs accidentally used as a single src.
    if url[0] in "[{":
        return ""
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("/")):
        return ""
    return url


_URL_IN_TEXT_RE = re.compile(r"https?://[^\s\]\"'<>]+", re.IGNORECASE)


def _extract_urls_from_text(text: str) -> List[str]:
    """Pull every http(s) URL out of a freeform / bracketed image cell."""
    out: List[str] = []
    seen: Set[str] = set()
    for match in _URL_IN_TEXT_RE.findall(text or ""):
        url = _clean_image_url(match.rstrip(".,;)]}"))
        if url and url not in seen:
            seen.add(url)
            out.append(url)
    return out


def _parse_image_list(raw: Any) -> List[str]:
    """Parse image fields that may be a URL, JSON list string, or list (like unit_images).

    Supports shapes like:
      - https://...
      - ["https://a", "https://b"]
      - [https://a, https://b, https://c]
      - ['https://a', 'https://b']
    """
    if raw is None:
        return []
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", errors="ignore")
    if isinstance(raw, (list, tuple)):
        out: List[str] = []
        seen: Set[str] = set()
        for part in raw:
            for url in _parse_image_list(part):
                if url not in seen:
                    seen.add(url)
                    out.append(url)
        return out
    if isinstance(raw, dict):
        for key in ("url", "src", "href", "image", "link"):
            url = _clean_image_url(raw.get(key))
            if url:
                return [url]
        return []
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return []
        if text[0] in "[{":
            try:
                parsed = json.loads(text)
            except Exception:
                parsed = None
            if parsed is not None:
                return _parse_image_list(parsed)
            # Bare / single-quoted list blobs: [url1, url2, ...]
            return _extract_urls_from_text(text)
        if "http://" in text or "https://" in text:
            found = _extract_urls_from_text(text)
            if found:
                return found
        url = _clean_image_url(text)
        return [url] if url else []
    return []


def _parse_amenities(raw: Any) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", errors="ignore")
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return []
        try:
            return _parse_amenities(json.loads(text))
        except Exception:
            return [
                part.strip()
                for part in text.replace("\n", ",").split(",")
                if part.strip()
            ]
    if isinstance(raw, (list, tuple)):
        out: List[str] = []
        for part in raw:
            text = _clean_text(part)
            if text and text not in out:
                out.append(text)
        return out
    return []


def _mysql_config() -> Dict[str, Any]:
    return {
        "host": os.environ.get("DB_HOST")
        or os.environ.get("MYSQL_HOST")
        or _DEFAULT_DB_HOST,
        "user": os.environ.get("DB_USER")
        or os.environ.get("MYSQL_USER")
        or _DEFAULT_DB_USER,
        "password": os.environ.get("DB_PASSWORD")
        or os.environ.get("MYSQL_PASSWORD")
        or _DEFAULT_DB_PASSWORD,
        "database": os.environ.get("DB_NAME")
        or os.environ.get("MYSQL_DATABASE")
        or _DEFAULT_DB_NAME,
        "port": int(os.environ.get("DB_PORT") or os.environ.get("MYSQL_PORT") or 3306),
    }


def fetch_featured_portfolio_names(connection: Any = None) -> List[str]:
    """Return portfolio names where portfolios.is_featured = 1."""
    owns_connection = connection is None
    conn = connection
    try:
        if owns_connection:
            conn = mysql.connector.connect(**_mysql_config())
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT portfolio
            FROM portfolios
            WHERE COALESCE(is_featured, 0) = 1
              AND portfolio IS NOT NULL
              AND TRIM(portfolio) <> ''
              AND TRIM(portfolio) <> '0'
            ORDER BY portfolio ASC
            """
        )
        rows = cursor.fetchall() or []
        cursor.close()

        names: List[str] = []
        seen: Set[str] = set()
        for row in rows:
            name = _first_non_empty((row or {}).get("portfolio"))
            key = _normalize_portfolio_name(name)
            if not key or key in seen:
                continue
            seen.add(key)
            names.append(name)
        return names
    except Exception as exc:
        print(f"Error fetching featured portfolios: {exc}")
        return []
    finally:
        if owns_connection and conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def fetch_featured_portfolio_buildings(
    connection: Any = None,
    *,
    dash_host: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return addresses under portfolios marked is_featured = 1."""
    owns_connection = connection is None
    conn = connection
    host = (dash_host or _DEFAULT_DASH_HOST).rstrip("/")
    try:
        if owns_connection:
            conn = mysql.connector.connect(**_mysql_config())
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                a.address_id,
                a.address,
                a.neighborhood,
                a.building_image,
                a.building_name,
                a.building_amenities,
                a.entity_id,
                e.entity AS entity_name,
                p.portfolio_id,
                p.portfolio AS portfolio_name
            FROM portfolios p
            INNER JOIN entities e
                ON e.portfolio_id = p.portfolio_id
            INNER JOIN addresses a
                ON CAST(a.entity_id AS UNSIGNED) = e.entity_id
            WHERE COALESCE(p.is_featured, 0) = 1
              AND a.address IS NOT NULL
              AND TRIM(a.address) <> ''
            ORDER BY p.portfolio ASC, a.address ASC
            """
        )
        rows = cursor.fetchall() or []
        cursor.close()

        buildings: List[Dict[str, Any]] = []
        seen: Set[str] = set()
        for row in rows:
            row = row or {}
            address = _first_non_empty(row.get("address"))
            if not address:
                continue
            address_id = row.get("address_id")
            dedupe_key = (
                str(address_id).strip()
                if address_id is not None and str(address_id).strip()
                else address.lower()
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            images = _parse_image_list(row.get("building_image"))
            if not images:
                images = [_coming_soon_image_for(address)]

            portfolio = _first_non_empty(row.get("portfolio_name"))
            buildings.append(
                {
                    "address_id": address_id,
                    "address": address,
                    "neighborhood": _first_non_empty(row.get("neighborhood")),
                    "building_name": _first_non_empty(row.get("building_name")),
                    "portfolio": portfolio,
                    "portfolio_id": row.get("portfolio_id"),
                    "entity_id": row.get("entity_id"),
                    "entity_name": _first_non_empty(row.get("entity_name")),
                    "images": images,
                    "amenities": _parse_amenities(row.get("building_amenities")),
                    "available_units": 0,
                    "price_from": None,
                    "bedrooms_label": "",
                    "schedule_tour_url": build_tour_schedule_url(
                        host,
                        address_id=address_id,
                    ),
                    "listings_url": (
                        f"/listings?v=2&address={quote(address)}"
                        + (f"&portfolio={quote(portfolio)}" if portfolio else "")
                    ),
                }
            )
        return buildings
    except Exception as exc:
        print(f"Error fetching featured portfolio buildings: {exc}")
        return []
    finally:
        if owns_connection and conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def _listing_images(listing: Dict[str, Any]) -> List[str]:
    """Unit-card images only: unit_images, then website_image. Never building photos."""
    images: List[str] = []
    seen: Set[str] = set()

    for url in _parse_image_list(listing.get("unit_images")):
        if url not in seen:
            seen.add(url)
            images.append(url)

    for url in _parse_image_list(listing.get("website_image")):
        if url not in seen:
            seen.add(url)
            images.append(url)

    return images


def _availability_label(listing: Dict[str, Any]) -> str:
    """Match listings_v2: Available Now, or Available on {move_out}."""
    move_out = _clean_text(listing.get("move_out"))
    if move_out.lower() in {"09/09/1999"}:
        move_out = ""
    if move_out:
        return f"Available on {move_out}"
    return "Available Now"


def _normalize_featured_listing(listing: Dict[str, Any]) -> Dict[str, Any]:
    item = dict(listing or {})
    images = _listing_images(item)
    item["unit_images"] = images
    item["featured_image"] = (
        images[0]
        if images
        else _coming_soon_image_for(item.get("unit_id") or item.get("id"))
    )
    item["availability_label"] = _availability_label(item)
    # Every listing in this strip already belongs to is_featured portfolios.
    item["is_featured_portfolio"] = True
    return item


def _listing_matches_featured(
    listing: Dict[str, Any],
    featured_names: Set[str],
    featured_addresses: Set[str],
    featured_address_ids: Set[str],
) -> bool:
    portfolio_key = _normalize_portfolio_name(listing.get("portfolio"))
    if portfolio_key and portfolio_key in featured_names:
        return True

    address = _first_non_empty(listing.get("address")).lower()
    if address and address in featured_addresses:
        return True

    address_id = listing.get("address_id")
    if address_id is not None and str(address_id).strip() in featured_address_ids:
        return True

    return False


def _listing_price(listing: Dict[str, Any]) -> Optional[float]:
    for key in ("actual_rent", "listed_net", "price"):
        value = listing.get(key)
        if value in (None, "", "N/A", "n/a", "-"):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _merge_listings(
    primary: List[Dict[str, Any]],
    secondary: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for listing in list(primary or []) + list(secondary or []):
        unit_id = str(listing.get("unit_id") or listing.get("id") or "").strip()
        dedupe = unit_id or (
            f"{_first_non_empty(listing.get('address')).lower()}|"
            f"{_first_non_empty(listing.get('unit')).lower()}"
        )
        if not dedupe or dedupe in seen:
            continue
        seen.add(dedupe)
        merged.append(listing)
    return merged


def fetch_listings_for_buildings(
    buildings: List[Dict[str, Any]],
    *,
    max_workers: int = 8,
) -> List[Dict[str, Any]]:
    """
    Load available units for featured buildings via parallel per-address Dash calls.

    Buildings themselves come from MySQL (fast). Inventory/stats need Dash; fan out
    by address in parallel so the homepage async enrich stays snappy.
    """
    if not buildings:
        return []

    try:
        from database import get_all_listings
    except Exception as exc:
        print(f"Unable to import get_all_listings for featured enrichment: {exc}")
        return []

    addresses: List[str] = []
    seen_addresses: Set[str] = set()
    for building in buildings:
        address = _first_non_empty(building.get("address"))
        key = address.lower()
        if not address or key in seen_addresses:
            continue
        seen_addresses.add(key)
        addresses.append(address)

    if not addresses:
        return []

    def _fetch_one(address: str) -> List[Dict[str, Any]]:
        try:
            return get_all_listings(address=address, available=True) or []
        except Exception as exc:
            print(f"Error fetching listings for featured address {address}: {exc}")
            return []

    collected: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    workers = max(1, min(int(max_workers or 8), len(addresses)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_fetch_one, address): address for address in addresses}
        for future in as_completed(futures):
            address = futures[future]
            try:
                rows = future.result() or []
            except Exception as exc:
                print(f"Error collecting listings for featured address {address}: {exc}")
                rows = []
            for listing in rows:
                unit_id = str(listing.get("unit_id") or listing.get("id") or "").strip()
                dedupe = unit_id or (
                    f"{address.lower()}|{_first_non_empty(listing.get('unit')).lower()}"
                )
                if not dedupe or dedupe in seen:
                    continue
                seen.add(dedupe)
                collected.append(listing)
    return collected


def _listing_beds(listing: Dict[str, Any]) -> Optional[int]:
    value = listing.get("beds")
    if value in (None, "", "N/A", "n/a", "-"):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _enrich_buildings_from_listings(
    buildings: List[Dict[str, Any]],
    listings: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    by_address: Dict[str, List[Dict[str, Any]]] = {}
    by_id: Dict[str, List[Dict[str, Any]]] = {}
    for listing in listings or []:
        address = _first_non_empty(listing.get("address")).lower()
        if address:
            by_address.setdefault(address, []).append(listing)
        address_id = listing.get("address_id")
        if address_id is not None and str(address_id).strip():
            by_id.setdefault(str(address_id).strip(), []).append(listing)

    enriched: List[Dict[str, Any]] = []
    for building in buildings:
        item = dict(building)
        matches = list(by_id.get(str(item.get("address_id") or "").strip(), []))
        if not matches:
            matches = list(
                by_address.get(_first_non_empty(item.get("address")).lower(), [])
            )

        item["available_units"] = len(matches)
        prices = [
            price
            for price in (_listing_price(listing) for listing in matches)
            if price is not None
        ]
        item["price_from"] = min(prices) if prices else None

        bedrooms = sorted(
            {
                beds
                for beds in (_listing_beds(listing) for listing in matches)
                if beds is not None
            }
        )
        if not bedrooms:
            item["bedrooms_label"] = ""
        elif len(bedrooms) == 1:
            beds = bedrooms[0]
            item["bedrooms_label"] = "Studio" if beds == 0 else f"{beds} Bed"
        else:
            low, high = bedrooms[0], bedrooms[-1]
            low_label = "Studio" if low == 0 else f"{low} Bed"
            high_label = f"{high} Bed"
            # Compact range for cards/modal (e.g. Studio - 3 Bed), even if a middle size is missing.
            item["bedrooms_label"] = f"{low_label} - {high_label}"

        # Keep address-level building_image only — never pull unit photos into building cards.
        enriched.append(item)
    return enriched


def select_featured_listings(
    listings: List[Dict[str, Any]],
    *,
    limit: int = 8,
    featured_portfolio_names: Optional[List[str]] = None,
    featured_buildings: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Keep only listings that belong to portfolios.is_featured = 1.

    No fill from other inventory.
    """
    names = featured_portfolio_names
    buildings = featured_buildings
    if names is None:
        names = fetch_featured_portfolio_names()
    if buildings is None:
        buildings = fetch_featured_portfolio_buildings()

    featured_names = {
        _normalize_portfolio_name(name)
        for name in (names or [])
        if _normalize_portfolio_name(name)
    }
    featured_addresses = {
        _first_non_empty(building.get("address")).lower()
        for building in (buildings or [])
        if _first_non_empty(building.get("address"))
    }
    featured_address_ids = {
        str(building.get("address_id")).strip()
        for building in (buildings or [])
        if building.get("address_id") is not None
        and str(building.get("address_id")).strip()
    }

    if not featured_names and not featured_addresses and not featured_address_ids:
        return []

    matched: List[Dict[str, Any]] = []
    for listing in listings or []:
        if not _listing_matches_featured(
            listing,
            featured_names,
            featured_addresses,
            featured_address_ids,
        ):
            continue
        matched.append(listing)

    # Prefer units with real unit_images, then any unit-level photo, for the homepage strip.
    matched.sort(
        key=lambda listing: (
            0 if _parse_image_list(listing.get("unit_images")) else (
                1 if _listing_images(listing) else 2
            ),
            str(listing.get("unit_id") or ""),
        )
    )

    selected: List[Dict[str, Any]] = []
    for listing in matched:
        selected.append(_normalize_featured_listing(listing))
        if len(selected) >= max(1, int(limit or 8)):
            break
    return selected


def get_homepage_featured_content(
    listings: Optional[List[Dict[str, Any]]] = None,
    *,
    listing_limit: int = 8,
    dash_host: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Return (featured_listings, featured_buildings) from is_featured only."""
    names = fetch_featured_portfolio_names()
    buildings = fetch_featured_portfolio_buildings(dash_host=dash_host)
    inventory = _merge_listings(
        listings or [],
        fetch_listings_for_buildings(buildings),
    )
    featured_listings = select_featured_listings(
        inventory,
        limit=listing_limit,
        featured_portfolio_names=names,
        featured_buildings=buildings,
    )
    featured_buildings = _enrich_buildings_from_listings(buildings, inventory)
    return featured_listings, featured_buildings
