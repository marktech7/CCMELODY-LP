import pytest
from unittest.mock import MagicMock

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings


def test_retrieve_live_item(flask_client):
    pytest.skip()
    res = flask_client.get('/api/v2/controller/live-item').get_json()
    assert len(res) == 0


def test_controller_set_requires_login(flask_client):
    pytest.skip('Need to figure out how to patch settings for one test only')
    # Settings().setValue('api/authentication enabled', True)
    res = flask_client.post('/api/v2/controller/show', json=dict())
    Settings().setValue('api/authentication enabled', False)
    assert res.status_code == 401


def test_controller_set_does_not_accept_get(flask_client):
    res = flask_client.get('/api/v2/controller/show')
    assert res.status_code == 405


def test_controller_set_calls_live_controller(flask_client):
    fake_live_controller = MagicMock()
    Registry.create().register('live_controller', fake_live_controller)
    res = flask_client.post('/api/v2/controller/show', json=dict(id=400))
    assert res.status_code == 204
    fake_live_controller.slidecontroller_live_set.emit.assert_called_once_with([400])


def test_controller_direction_requires_login(flask_client):
    Settings().setValue('api/authentication enabled', True)
    res = flask_client.post('/api/v2/controller/progress', json=dict())
    Settings().setValue('api/authentication enabled', False)
    assert res.status_code == 401


def test_controller_direction_does_not_accept_get(flask_client):
    res = flask_client.get('/api/v2/controller/progress')
    assert res.status_code == 405


def test_controller_direction_does_fails_on_wrong_data(flask_client):
    res = flask_client.post('/api/v2/controller/progress', json=dict(action='foo'))
    assert res.status_code == 400


def test_controller_direction_calls_service_manager(flask_client):
    fake_live_controller = MagicMock()
    Registry.create().register('live_controller', fake_live_controller)
    res = flask_client.post('/api/v2/controller/progress', json=dict(action='next'))
    assert res.status_code == 204
    fake_live_controller.slidecontroller_live_next.emit.assert_called_once()
