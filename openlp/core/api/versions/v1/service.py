from openlp.core.api.lib import old_auth, old_success_response, extract_request
from flask import jsonify, request, Blueprint

from openlp.core.common.registry import Registry

service_views = Blueprint('old_service', __name__)


@service_views.route('/api/service/list')
def service_items():
    live_controller = Registry().get('live_controller')
    service_items = []
    if live_controller.service_item:
        current_unique_identifier = live_controller.service_item.unique_identifier
    else:
        current_unique_identifier = None
    for item in Registry().get('service_manager').service_items:
        service_item = item['service_item']
        service_items.append({
            'id': str(service_item.unique_identifier),
            'title': str(service_item.get_display_title()),
            'plugin': str(service_item.name),
            'notes': str(service_item.notes),
            'selected': (service_item.unique_identifier == current_unique_identifier)
        })
    return jsonify({'results': {'items': service_items}})


@service_views.route('/api/service/set')
@old_auth
def service_set():
    event = Registry().get('service_manager').servicemanager_set_item
    try:
        data = int(extract_request(request.args.get('data', ''), 'id'))
        event.emit(data)
    except (KeyError, ValueError):
        pass
    return old_success_response()


@service_views.route('/api/service/direction/<action>')
@old_auth
def service_direction(action):
    ALLOWED_ACTIONS = ['next', 'previous']
    action = action.lower()
    if action in ALLOWED_ACTIONS:
        getattr(Registry().get('service_manager'), 'servicemanager_{action}_item'.format(action=action)).emit()
    return old_success_response()
