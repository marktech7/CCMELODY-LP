from openlp.core.api.versions.v1.controller import controller_views
from openlp.core.api.versions.v1.core import core_views
from openlp.core.api.versions.v1.service import service_views


def register_blueprints(app):
    app.register_blueprint(controller_views)
    app.register_blueprint(core_views)
    app.register_blueprint(service_views)
