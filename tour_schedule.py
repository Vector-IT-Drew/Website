"""Helpers for Dash tour-schedule and rental-application deep links."""

from urllib.parse import quote, urlencode


def build_tour_schedule_url(dash_host, unit_id=None, address_id=None, email_address=None):
    """
    Build a Dash tour-schedule URL.

    Priority: unit_id (listing page) > address_id (building page) > general CTA.
    Dash resolves portfolio email from unit_id/address_id; only pass email_address
    as an explicit override when no ID is available (e.g. portfolio-only CTAs).
    """
    base = f"{dash_host.rstrip('/')}/tour-schedule"
    params = {}

    if unit_id is not None and str(unit_id).strip():
        params['unit_id'] = str(unit_id).strip()
    elif address_id is not None and str(address_id).strip():
        params['address_id'] = str(address_id).strip()

    if email_address and str(email_address).strip():
        params['email_address'] = str(email_address).strip()

    if not params:
        return base

    return f"{base}?{urlencode(params, quote_via=quote)}"


def build_rental_application_url(dash_host, unit_id=None):
    """
    Build a Dash rental-application URL for a unit.

    Example:
    https://dash-production-b25c.up.railway.app/rental-app/rental-application?unit_id=5496
    """
    base = f"{dash_host.rstrip('/')}/rental-app/rental-application"
    if unit_id is None or not str(unit_id).strip():
        return base
    return f"{base}?{urlencode({'unit_id': str(unit_id).strip()}, quote_via=quote)}"
