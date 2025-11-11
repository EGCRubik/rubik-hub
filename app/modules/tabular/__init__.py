from core.blueprints.base_blueprint import BaseBlueprint

from flask_restful import Api
from app.modules.dataset.api import init_blueprint_api

tabular_bp = BaseBlueprint("tabular", __name__, template_folder="templates", url_prefix="/tabular")

api = Api(tabular_bp)
init_blueprint_api(tabular_bp)

