from openlp.core.api.versions.v2.controller import controller_views
from openlp.core.api.versions.v2.core import core
from openlp.core.api.versions.v2.service import service_views


def register_blueprints(app):
    app.register_blueprint(controller_views, url_prefix='/api/v2/controller/')
    app.register_blueprint(core, url_prefix='/api/v2/core/')
    app.register_blueprint(service_views, url_prefix='/api/v2/service/')
