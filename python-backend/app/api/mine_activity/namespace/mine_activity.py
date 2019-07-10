from flask_restplus import Namespace
from app.api.mine_activity.resources.mine_activity import MineActivityResource

api = Namespace('activity', description='Search related operations')

api.add_resource(MineActivityResource, '/mine/<string:mine_guid>')