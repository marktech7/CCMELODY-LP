import pytest
from unittest.mock import MagicMock

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings


def test_retrieve_service_items(flask_client):
    pytest.skip()
    res = flask_client.get('/api/v2/service/items').get_json()
    assert len(res) == 0


def test_service_set_requires_login(flask_client):
    Settings().setValue('api/authentication enabled', True)
    res = flask_client.post('/api/v2/service/show', json=dict())
    Settings().setValue('api/authentication enabled', False)
    assert res.status_code == 401


def test_service_set_does_not_accept_get(flask_client):
    res = flask_client.get('/api/v2/service/show')
    assert res.status_code == 405


def test_service_set_calls_service_manager(flask_client):
    fake_service_manager = MagicMock()
    Registry.create().register('service_manager', fake_service_manager)
    res = flask_client.post('/api/v2/service/show', json=dict(id=400))
    assert res.status_code == 204
    fake_service_manager.set_item.assert_called_once_with(400)


def test_service_direction_requires_login(flask_client):
    Settings().setValue('api/authentication enabled', True)
    res = flask_client.post('/api/v2/service/progress', json=dict())
    Settings().setValue('api/authentication enabled', False)
    assert res.status_code == 401


def test_service_direction_does_not_accept_get(flask_client):
    res = flask_client.get('/api/v2/service/progress')
    assert res.status_code == 405


def test_service_direction_does_fails_on_wrong_data(flask_client):
    res = flask_client.post('/api/v2/service/progress', json=dict(action='foo'))
    assert res.status_code == 400


def test_service_direction_calls_service_manager(flask_client):
    fake_service_manager = MagicMock()
    Registry.create().register('service_manager', fake_service_manager)
    res = flask_client.post('/api/v2/service/progress', json=dict(action='next'))
    assert res.status_code == 204
    fake_service_manager.servicemanager_next_item.emit.assert_called_once()
