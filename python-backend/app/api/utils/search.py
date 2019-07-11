from sqlalchemy import desc, or_, func
from app.extensions import db
from datetime import datetime, timedelta

from app.api.mines.mine.models.mine import Mine
from app.api.parties.party.models.party import Party
from app.api.mines.permits.permit.models.permit import Permit
from app.api.documents.mines.models.mine_document import MineDocument
from app.api.variances.models.variance import Variance
from app.api.mines.incidents.models.mine_incident import MineIncident
from app.api.mines.permits.permit_amendment.models.permit_amendment_document import PermitAmendmentDocument

common_search_targets = {
    'mine': {
        'model': Mine,
        'primary_column': Mine.mine_guid,
        'description': 'Mines',
        'entities_to_return': [Mine.mine_guid, Mine.mine_no, Mine.mine_name],
        'columns_to_search': [Mine.mine_name, Mine.mine_no],
        'has_deleted_ind': True,
        'id_field': 'mine_guid',
        'value_field': 'mine_name',
        'score_multiplier': 500
    },
    'party': {
        'model':
        Party,
        'primary_column': Party.party_guid,
        'description':
        'Contacts',
        'entities_to_return': [
            Party.party_guid,
            func.concat(Party.first_name, ' ', Party.party_name).label('name'), Party.email
        ],
        'columns_to_search': [Party.first_name, Party.party_name, Party.email, Party.phone_no],
        'has_deleted_ind':
        True,
        'id_field':
        'party_guid',
        'value_field':
        'name',
        'score_multiplier':
        150
    }
}

simple_additional_search_targets = {
    'permit': {
        'model': Permit,
        'primary_column': Permit.permit_guid,
        'description': 'Permits',
        'entities_to_return': [Permit.permit_guid, Permit.mine_guid, Permit.permit_no],
        'columns_to_search': [Permit.permit_no],
        'has_deleted_ind': False,
        'id_field': 'mine_guid',
        'value_field': 'permit_no',
        'score_multiplier': 1000
    }
}

full_additional_search_targets = {
    'permit': {
        'model': Permit,
        'primary_column': Permit.permit_guid,
        'description': 'Permits',
        'entities_to_return': [Permit.permit_guid, Permit.permit_no],
        'columns_to_search': [Permit.permit_no],
        'has_deleted_ind': False,
        'id_field': 'permit_guid',
        'value_field': 'permit_no',
        'score_multiplier': 1000
    },
    'mine_documents': {
        'model': MineDocument,
        'primary_column': MineDocument.mine_document_guid,
        'description': 'Mine Documents',
        'entities_to_return': [MineDocument.mine_document_guid, MineDocument.document_name],
        'columns_to_search': [MineDocument.document_name],
        'has_deleted_ind': False,
        'id_field': 'mine_document_guid',
        'value_field': 'document_name',
        'score_multiplier': 250
    },
    'permit_documents': {
        'model': PermitAmendmentDocument,
        'primary_column': PermitAmendmentDocument.permit_amendment_document_guid,
        'description': 'Permit Documents',
        'entities_to_return': [PermitAmendmentDocument.permit_amendment_document_guid, PermitAmendmentDocument.document_name],
        'columns_to_search': [PermitAmendmentDocument.document_name],
        'has_deleted_ind': False,
        'id_field': 'permit_amendment_document_guid',
        'value_field': 'document_name',
        'score_multiplier': 250
    }
}

activity_search_targets = {
    'mine': {
        'model': Mine,
        'primary_column': Mine.mine_guid,
        'description': 'Mines',
        'entities_to_return': [Mine.mine_guid, Mine.mine_no, Mine.mine_name, Mine.update_timestamp, Mine.update_user],
        'has_deleted_ind': True,
        'id_field': 'mine_guid',
        'value_field': 'mine_name',
        'join_model': None,
        'message': 'Mine information changed.'
    },
    'permit': {
        'model': Permit,
        'primary_column': Permit.permit_guid,
        'description': 'Permits',
        'entities_to_return': [Permit.permit_guid, Permit.permit_no, Permit.update_timestamp, Permit.update_user],
        'has_deleted_ind': False,
        'id_field': 'permit_guid',
        'value_field': 'permit_no',
        'join_model': None,
        'message': 'Permit information was changed.'
    },
    # 'variance': {
    #     'model': Variance,
    #     'primary_column': Variance.variance_id,
    #     'description': 'Variance',
    #     'entities_to_return': [Variance.variance_id, Variance.update_user, Variance.update_timestamp],
    #     'has_deleted_ind': False,
    #     'id_field': 'variance_id',
    #     'value_field': 'variance_id',
        # 'join_model': None,
    #     'message': 'Variance  information was changed.'
    # },
    'mine_incident': {
        'model': MineIncident,
        'primary_column': MineIncident.mine_incident_id,
        'description': 'Mine Incident',
        'entities_to_return': [MineIncident.mine_incident_id, MineIncident.update_user, MineIncident.update_timestamp],
        'has_deleted_ind': False,
        'id_field': 'mine_incident_id',
        'value_field': 'report_name',
        'join_model': None,
        'message': f'Mine Incident was changed.'
    },
}

simple_search_targets = dict(**common_search_targets, **simple_additional_search_targets)
search_targets = dict(**common_search_targets, **full_additional_search_targets)

def append_result(search_results, search_term, type, item, id_field, value_field, score_multiplier):

    # Find matches that start with the search term and apply a multiplier
    if getattr(item, value_field).lower().startswith(search_term.lower()):
        score_multiplier = score_multiplier * 3

    # Find matches that exactly match the search term and apply a multiplier
    if getattr(item, value_field).lower() == search_term.lower():
        score_multiplier = score_multiplier * 10

    search_results.append(
        SearchResult(
            getattr(item, 'score') * score_multiplier, type, {
                'id': getattr(item, id_field),
                'value': getattr(item, value_field)
            }))


def execute_search(app, search_results, search_term, search_terms, type, type_config, limit_results=None):
    with app.app_context():
        for term in search_terms:
            if len(term) > 2:
                for column in type_config['columns_to_search']:

                    # Query should return with the calculated column "score", as well as the columns defined in the configuration 
                    similarity = db.session.query(type_config['model']).with_entities(
                        func.similarity(column, term).label('score'),
                        *type_config['entities_to_return']).filter(column.ilike(f'%{term}%'))

                    if type_config['has_deleted_ind']:
                        similarity = similarity.filter_by(deleted_ind=False)

                    similarity = similarity.order_by(desc(func.similarity(column, term)))
                    
                    if limit_results:
                        similarity = similarity.limit(limit_results)

                    similarity = similarity.all()

                    for item in similarity:
                        append_result(search_results, search_term, type, item,
                                      type_config['id_field'], type_config['value_field'],
                                      type_config['score_multiplier'])

def execute_activity_search(app, search_results, type, type_config, mine_guid, join_model=None, limit_results=None):
    with app.app_context():
        activity = db.session.query(type_config['model']).with_entities(
            *type_config['entities_to_return']).filter(type_config['model'].update_timestamp > (datetime.today() - timedelta(days=30)), type_config['model'].mine_guid == mine_guid)

        if type_config['has_deleted_ind']:
            activity = activity.filter_by(deleted_ind=False)
        if type_config['join_model']:
            activity = activity.join(type_config['join_model'])

        activity = activity.order_by(desc(type_config['model'].update_timestamp))
        
        if limit_results:
            activity = activity.limit(limit_results)

        activity = activity.all()

        for item in activity:
            search_results.append(SearchResult(None, type, {
                'date_changed': item.update_timestamp, 
                'description': type_config['message'],
                'user': item.update_user
                }
                )
            )

class SearchResult:
    def __init__(self, score, type, result):
        self.score = score
        self.type = type
        self.result = result

    def json(self):
        return {'score': self.score, 'type': self.type, 'result': self.result}
