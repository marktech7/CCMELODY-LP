from flask import Blueprint, send_from_directory
from openlp.core.common.applocation import AppLocation

main_views = Blueprint('main', __name__)


@main_views.route('/')
def index():
    return send_from_directory(str(AppLocation.get_section_data_path('remotes')), 'index.html')


@main_views.route('/<path>')
def assets(path):
    return send_from_directory(str(AppLocation.get_section_data_path('remotes')), path)
