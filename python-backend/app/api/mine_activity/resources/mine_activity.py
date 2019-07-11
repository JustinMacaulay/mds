import regex
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask_restplus import Resource, fields
from app.extensions import api
from flask import request, current_app
from datetime import datetime, timedelta

from app.extensions import db, api
from app.api.utils.access_decorators import requires_role_view_all, requires_role_mine_edit
from app.api.utils.resources_mixins import UserMixin, ErrorMixin
from app.api.utils.search import append_result, execute_activity_search, activity_search_targets

MINE_ACTIVITY_MODEL = api.model('MineActivity', {
    'date': fields.Date,
    'message': fields.String,
    'user': fields.String,
})


class MineActivityResource(Resource, UserMixin):
    @requires_role_view_all
    @api.marshal_with(MINE_ACTIVITY_MODEL, envelope='records', code=200)
    def get(self, mine_guid):
        search_results = []
        app = current_app._get_current_object()

        search_types = activity_search_targets.keys()

        with ThreadPoolExecutor(max_workers=50) as executor:
            task_list = []
            for type, type_config in activity_search_targets.items():
                if type in search_types:
                    task_list.append(
                        executor.submit(execute_activity_search, app, search_results, type,
                                        type_config, mine_guid))
            for task in as_completed(task_list):
                try:
                    data = task.result()
                except Exception as exc:
                    current_app.logger.error(f'generated an exception: {exc}')

        all_search_results = []
        for result in search_results:
            all_search_results.append({
                'date': result.result.get('date_changed'),
                'message': result.result.get('description'),
                'user': result.result.get('user')
            })
        # for type in search_types:
        #     top_search_results_by_type = {}

        #     max_results = 5
        #     if len(search_types) == 1:
        #         max_results = 50

        #     for result in top_search_results:
        #         if len(top_search_results_by_type) > max_results:
        #             break
        #         if result.type == type:
        #             top_search_results_by_type[result.result['id']] = result

        #     full_results = db.session.query(search_targets[type]['model']).filter(
        #         search_targets[type]['primary_column'].in_(
        #             top_search_results_by_type.keys())).all()

        #     for full_result in full_results:
        #         top_search_results_by_type[getattr(
        #             full_result, search_targets[type]['id_field'])].result = full_result

        #     all_search_results[type] = list(top_search_results_by_type.values())

        return sorted(all_search_results, key=lambda x: x['date'], reverse=True)
