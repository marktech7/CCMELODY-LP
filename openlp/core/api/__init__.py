# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2020 OpenLP Developers                              #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################

from flask import Flask
from flask_cors import CORS

from openlp.core.api.versions import v1
from openlp.core.api.versions import v2
from openlp.core.api.main import main_views

app = Flask(__name__)
CORS(app)

app.register_blueprint(main_views)
v1.register_blueprints(app)
v2.register_blueprints(app)


def register_blueprint(blueprint, url_prefix=None):
    app.register_blueprint(blueprint, url_prefix)
