import database


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self):
        return self._payload


def test_get_all_listings_falls_back_to_address_fanout_when_dash_unfiltered_errors(monkeypatch):
    calls = []

    def fake_get(url, params=None, timeout=None):
        params = params or {}
        calls.append((url, dict(params)))
        if url.endswith('/unique-values'):
            return _FakeResponse({
                'status': 'success',
                'unique_addresses': ['1113 York Avenue', '525 East 72nd Street'],
                'unique_neighborhoods': [],
            })
        if url.endswith('/get_filtered_listings'):
            # Broad/unfiltered-style calls fail the way production Dash currently does.
            if 'address' not in params:
                return _FakeResponse({
                    'status': 'error',
                    'message': "name '_format_listing_move_out' is not defined",
                })
            address = params['address']
            if address == '1113 York Avenue':
                return _FakeResponse({
                    'status': 'success',
                    'data': [{
                        'listing_id': 1,
                        'unit_id': 101,
                        'address': '1113 York Avenue',
                        'unit': '036B',
                        'listed_net': 9500,
                        'beds': 2,
                        'baths': 2,
                    }],
                })
            if address == '525 East 72nd Street':
                return _FakeResponse({
                    'status': 'success',
                    'data': [{
                        'listing_id': 2,
                        'unit_id': 202,
                        'address': '525 East 72nd Street',
                        'unit': '12A',
                        'listed_net': 8850,
                        'beds': 2,
                        'baths': 2,
                    }],
                })
        return _FakeResponse({'status': 'error', 'message': 'unexpected'})

    monkeypatch.setattr(database.requests, 'get', fake_get)

    listings = database.get_all_listings()
    assert len(listings) == 2
    assert {row['unit_id'] for row in listings} == {'101', '202'}
    assert any(url.endswith('/unique-values') for url, _ in calls)
    assert all(
        params.get('available') == 'true'
        for url, params in calls
        if url.endswith('/get_filtered_listings') and 'address' in params
    )


def test_get_all_listings_scoped_address_uses_data_payload(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        assert params['address'] == '1113 York Avenue'
        assert params['available'] == 'true'
        return _FakeResponse({
            'status': 'success',
            'data': [{
                'listing_id': 9,
                'unit_id': 909,
                'address': '1113 York Avenue',
                'unit': '1A',
                'listed_net': 4000,
                'beds': 1,
                'baths': 1,
            }],
        })

    monkeypatch.setattr(database.requests, 'get', fake_get)
    listings = database.get_all_listings(address='1113 York Avenue', available=True)
    assert len(listings) == 1
    assert listings[0]['unit_id'] == '909'
    assert listings[0]['address'] == '1113 York Avenue'


def test_listings_route_does_not_force_available_false(monkeypatch):
    captured = {}

    def fake_get_all_listings(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr('app.get_all_listings', fake_get_all_listings)
    monkeypatch.setattr('app.requests.get', lambda *args, **kwargs: _FakeResponse({
        'unique_neighborhoods': [],
        'unique_addresses': [],
    }))

    from app import app
    client = app.test_client()
    resp = client.get('/listings?v=2')
    assert resp.status_code == 200
    assert captured.get('available') is None

    resp = client.get('/listings?v=2&availability=available')
    assert resp.status_code == 200
    assert captured.get('available') is True
