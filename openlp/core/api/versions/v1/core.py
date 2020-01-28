from openlp.core.api.lib import old_auth, old_success_response
from openlp.core.common.registry import Registry
from openlp.core.lib import image_to_byte
from openlp.core.lib.plugin import PluginStatus, StringContent
from openlp.core.state import State

from flask import jsonify, Blueprint


core_views = Blueprint('old_core', __name__)


@core_views.route('/api/poll')
def poll():
    return jsonify(Registry().get('poller').poll())


@core_views.route('/api/display/<display>')
@old_auth
def toggle_display(display):
    ALLOWED_ACTIONS = ['hide', 'show', 'blank', 'theme', 'desktop']
    display = display.lower()
    if display in ALLOWED_ACTIONS:
        Registry().get('live_controller').slidecontroller_toggle_display.emit(display)
    return old_success_response()


@core_views.route('/api/plugin/search')
def plugin_list():
    searches = []
    for plugin in State().list_plugins():
        if plugin.status == PluginStatus.Active and plugin.media_item and plugin.media_item.has_search:
            searches.append([plugin.name, str(plugin.text_strings[StringContent.Name]['plural'])])
    return jsonify({'results': {'items': searches}})


@core_views.route('/main/image')
def main_image():
    img = 'data:image/png;base64,{}'.format(image_to_byte(Registry().get('live_controller').grab_maindisplay()))
    return jsonify({'slide_image': img})
