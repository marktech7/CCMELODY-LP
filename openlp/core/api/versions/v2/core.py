from openlp.core.api.lib import login_required
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.core.lib import image_to_byte
from openlp.core.lib.plugin import PluginStatus, StringContent
from openlp.core.state import State

from flask import jsonify, request, abort, Blueprint


core = Blueprint('core', __name__)


@core.route('/poll')
def poll():
    return jsonify(Registry().get('poller').poll())


@core.route('/display', methods=['POST'])
@login_required
def toggle_display():
    ALLOWED_ACTIONS = ['hide', 'show', 'blank', 'theme', 'desktop']
    data = request.json
    if not data:
        abort(400)
    display = data.get('display', '').lower()
    if display not in ALLOWED_ACTIONS:
        abort(400)

    Registry().get('live_controller').slidecontroller_toggle_display.emit(display)
    return '', 204


@core.route('/plugins')
def plugin_list():
    searches = []
    for plugin in State().list_plugins():
        if plugin.status == PluginStatus.Active and plugin.media_item and plugin.media_item.has_search:
            searches.append({'key': plugin.name, 'name': str(plugin.text_strings[StringContent.Name]['plural'])})
    return jsonify(searches)


@core.route('/system')
def system_information():
    data = {}
    data['websocket_port'] = Settings().value('api/websocket port')
    data['login_required'] = Settings().value('api/authentication enabled')
    return jsonify(data)


@core.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        abort(400)
    username = data.get('username', '')
    password = data.get('password', '')
    if username == Settings().value('api/user id') and password == Settings().value('api/password'):
        return jsonify({'token': Registry().get('authentication_token')})
    else:
        return '', 401


@core.route('/live-image')
def main_image():
    controller = Registry().get('live_controller')
    img = 'data:image/png;base64,{}'.format(image_to_byte(controller.grab_maindisplay()))
    return jsonify({'binary_image': img})
