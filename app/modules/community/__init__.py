from flask_restful import Api

from app.modules.dataset.api import init_blueprint_api
from core.blueprints.base_blueprint import BaseBlueprint

community_bp = BaseBlueprint('community', __name__, template_folder='templates')

api = Api(community_bp)
init_blueprint_api(community_bp)