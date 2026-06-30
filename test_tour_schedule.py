from tour_schedule import build_tour_schedule_url

DASH_HOST = 'https://dash.example.com'


def test_listing_page_url():
    url = build_tour_schedule_url(DASH_HOST, unit_id=344)
    assert url == 'https://dash.example.com/tour-schedule?unit_id=344'


def test_optional_email_override():
    url = build_tour_schedule_url(DASH_HOST, email_address='leasing@portfolio.com')
    assert url == 'https://dash.example.com/tour-schedule?email_address=leasing%40portfolio.com'


def test_building_page_url():
    url = build_tour_schedule_url(DASH_HOST, address_id=534)
    assert url == 'https://dash.example.com/tour-schedule?address_id=534'


def test_general_tour_url():
    url = build_tour_schedule_url(DASH_HOST)
    assert url == 'https://dash.example.com/tour-schedule'


def test_unit_id_takes_priority_over_address_id():
    url = build_tour_schedule_url(DASH_HOST, unit_id=344, address_id=534)
    assert 'unit_id=344' in url
    assert 'address_id' not in url
