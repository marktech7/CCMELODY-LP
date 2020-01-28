import os
import urllib.request
from pathlib import Path

from openlp.core.api.lib import login_required
from openlp.core.common import ThemeLevel
from openlp.core.common.registry import Registry
from openlp.core.common.applocation import AppLocation
from openlp.core.common.settings import Settings
from openlp.core.lib import create_thumb
from openlp.core.lib.serviceitem import ItemCapabilities

from flask import jsonify, request, abort, Blueprint

controller_views = Blueprint('controller', __name__)


@controller_views.route('/live-item')
def controller_text_api():
    live_controller = Registry().get('live_controller')
    current_item = live_controller.service_item
    data = []
    if current_item:
        for index, frame in enumerate(current_item.get_frames()):
            item = {}
            item['tag'] = index + 1
            item['selected'] = live_controller.selected_row == index
            item['title'] = current_item.title
            if current_item.is_text():
                if frame['verse']:
                    item['tag'] = str(frame['verse'])
                item['chords_text'] = str(frame.get('chords_text', ''))
                item['text'] = frame['text']
                item['html'] = current_item.get_rendered_frame(index)
            elif current_item.is_image() and not frame.get('image', '') and Settings().value('api/thumbnails'):
                thumbnail_path = os.path.join('images', 'thumbnails', frame['title'])
                full_thumbnail_path = AppLocation.get_data_path() / thumbnail_path
                if not full_thumbnail_path.exists():
                    create_thumb(Path(current_item.get_frame_path(index)), full_thumbnail_path, False)
                Registry().get('image_manager').add_image(str(full_thumbnail_path), frame['title'], None, 88, 88)
                item['img'] = urllib.request.pathname2url(os.path.sep + str(thumbnail_path))
                item['text'] = str(frame['title'])
                item['html'] = str(frame['title'])
            else:
                # presentations and other things
                if current_item.is_capable(ItemCapabilities.HasDisplayTitle):
                    item['title'] = str(frame['display_title'])
                if current_item.is_capable(ItemCapabilities.HasNotes):
                    item['slide_notes'] = str(frame['notes'])
                if current_item.is_capable(ItemCapabilities.HasThumbnails) and Settings().value('api/thumbnails'):
                    # If the file is under our app directory tree send the portion after the match
                    data_path = str(AppLocation.get_data_path())
                    if frame['image'][0:len(data_path)] == data_path:
                        item['img'] = urllib.request.pathname2url(frame['image'][len(data_path):])
                    Registry().get('image_manager').add_image(frame['image'], frame['title'], None, 88, 88)
                item['text'] = str(frame['title'])
                item['html'] = str(frame['title'])
            data.append(item)
    return jsonify(data)


@controller_views.route('/show', methods=['POST'])
@login_required
def controller_set():
    data = request.json
    if not data:
        abort(400)
    num = data.get('id', -1)
    Registry().get('live_controller').slidecontroller_live_set.emit([num])
    return '', 204


@controller_views.route('/progress', methods=['POST'])
@login_required
def controller_direction():
    ALLOWED_ACTIONS = ['next', 'previous']
    data = request.json
    if not data:
        abort(400)
    action = data.get('action', '').lower()
    if action not in ALLOWED_ACTIONS:
        abort(400)
    getattr(Registry().get('live_controller'), 'slidecontroller_live_{action}'.
            format(action=action)).emit()
    return '', 204


@controller_views.route('/get_theme_level', methods=['GET'])
@login_required
def get_theme_level():
    theme_level = Settings().value('themes/theme level')

    if theme_level == ThemeLevel.Global:
        theme_level = 'global'
    elif theme_level == ThemeLevel.Service:
        theme_level = 'service'
    elif theme_level == ThemeLevel.Song:
        theme_level = 'song'

    return jsonify(theme_level)


@controller_views.route('/set_theme_level', methods=['POST'])
@login_required
def set_theme_level():
    data = request.json
    theme_level = ''

    try:
        theme_level = str(data.get("level"))
    except ValueError:
        abort(400)

    if theme_level == 'global':
        Settings().setValue('themes/theme level', 1)
    elif theme_level == 'service':
        Settings().setValue('themes/theme level', 2)
    elif theme_level == 'song':
        Settings().setValue('theme/theme level', 3)

    return '', 204


@controller_views.route('/themes', methods=['GET'])
@login_required
def get_themes():
    theme_level = Settings().value('themes/theme level')
    theme_list = []
    current_theme = ''

    if theme_level == ThemeLevel.Global:
        current_theme = Registry().get('theme_manager').global_theme
    if theme_level == ThemeLevel.Service:
        current_theme = Registry().get('service_manager').service_theme

    # Gets and appends theme list
    for theme in Registry().execute('get_theme_names')[0]:
        theme_list.append({
            'name': theme,
            'selected': False
        })
    for i in theme_list:
        if i["name"] == current_theme:
            i["selected"] = True

    return jsonify(theme_list)


@controller_views.route('/theme_change', methods=['POST'])
@login_required
def set_theme():
    data = request.json
    theme = ''
    theme_level = Settings().value('themes/theme level')

    if not data:
        abort(400)
    try:
        theme = str(data.get('theme'))
    except ValueError:
        abort(400)

    if theme_level == ThemeLevel.Global:
        Settings().setValue('themes/global theme', theme)
        Registry().execute('theme_update_global')
    elif theme_level == ThemeLevel.Service:
        Settings().setValue('servicemanager/service theme', theme)
        Registry().execute('theme_update_service')

    return '', 204
