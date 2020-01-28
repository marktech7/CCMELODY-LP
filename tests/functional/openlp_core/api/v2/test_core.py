from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.state import State
from openlp.core.lib.plugin import PluginStatus, StringContent


def test_plugins_returns_list(flask_client):
    State().load_settings()
    res = flask_client.get('/api/v2/core/plugins').get_json()
    assert len(res) == 0

    class FakeMediaItem:
        has_search = True

    class FakePlugin:
        name = 'Faked'
        is_plugin = True
        status = PluginStatus.Active
        media_item = FakeMediaItem()
        text_strings = {StringContent.Name: {'plural': 'just a text'}}
    plugin = FakePlugin()
    State().modules['testplug'] = plugin
    Registry.create().register('testplug_plugin', plugin)
    res = flask_client.get('/api/v2/core/plugins').get_json()
    assert len(res) == 1
    assert res[0]['key'] == plugin.name
    assert res[0]['name'] == plugin.text_strings[StringContent.Name]['plural']


def test_system_information(flask_client, settings):
    Settings().setValue('api/authentication enabled', False)
    res = flask_client.get('/api/v2/core/system').get_json()
    assert res['websocket_port'] > 0
    assert not res['login_required']


def test_poll(flask_client):
    class FakePoller:
        def poll(self):
            return {'foo': 'bar'}
    Registry.create().register('poller', FakePoller())
    res = flask_client.get('/api/v2/core/poll').get_json()
    assert res['foo'] == 'bar'


def test_login_get_is_refused(flask_client):
    res = flask_client.get('/api/v2/core/login')
    assert res.status_code == 405


def test_login_without_data_returns_400(flask_client):
    res = flask_client.post('/api/v2/core/login')
    assert res.status_code == 400


def test_login_with_invalid_credetials_returns_401(flask_client, settings):
    res = flask_client.post('/api/v2/core/login', json=dict(username='openlp', password='invalid'))
    assert res.status_code == 401


def test_login_with_valid_credetials_returns_token(flask_client, settings):
    Registry().register('authentication_token', 'foobar')
    res = flask_client.post('/api/v2/core/login', json=dict(username='openlp', password='password'))
    assert res.status_code == 200
    assert res.get_json()['token'] == 'foobar'


def test_retrieving_image(flask_client):
    class FakeController:
        def grab_maindisplay(self):
            class FakeImage:
                def save(self, first, second):
                    pass
            return FakeImage()
    Registry.create().register('live_controller', FakeController())
    res = flask_client.get('/api/v2/core/live-image').get_json()
    assert res['binary_image'] != ''


def test_toggle_display_requires_login(flask_client, settings):
    Settings().setValue('api/authentication enabled', True)
    res = flask_client.post('/api/v2/core/display')
    Settings().setValue('api/authentication enabled', False)
    assert res.status_code == 401


def test_toggle_display_does_not_allow_get(flask_client):
    res = flask_client.get('/api/v2/core/display')
    assert res.status_code == 405


def test_toggle_display_invalid_action(flask_client, settings):
    res = flask_client.post('/api/v2/core/display', json={'display': 'foo'})
    assert res.status_code == 400


def test_toggle_display_valid_action_updates_controller(flask_client, settings):
    class FakeController:
        class Emitter:
            def emit(self, value):
                self.set = value
        slidecontroller_toggle_display = Emitter()
    controller = FakeController()
    Registry().register('live_controller', controller)
    res = flask_client.post('/api/v2/core/display', json={'display': 'show'})
    assert res.status_code == 204
    assert controller.slidecontroller_toggle_display.set == 'show'


def test_cors_headers_are_present(flask_client):
    res = flask_client.get('/api/v2/core/system')
    assert 'Access-Control-Allow-Origin' in res.headers
    assert res.headers['Access-Control-Allow-Origin'] == '*'
