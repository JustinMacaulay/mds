import json
import uuid
import pytest

from tests.factories import MineFactory, MineReportFactory, PermitFactory, PermitAmendmentFactory, PartyFactory


# GET
def test_get_permit_not_found(test_client, db_session, auth_headers):
    get_resp = test_client.get(f'/permits/{uuid.uuid4()}', headers=auth_headers['full_auth_header'])
    get_data = json.loads(get_resp.data.decode())
    assert 'not found' in get_data['message']
    assert get_resp.status_code == 404


def test_get_permit(test_client, db_session, auth_headers):
    permit_guid = PermitFactory().permit_guid

    get_resp = test_client.get(f'/permits/{permit_guid}', headers=auth_headers['full_auth_header'])
    get_data = json.loads(get_resp.data.decode())
    assert get_data['permit_guid'] == str(permit_guid)
    assert get_resp.status_code == 200


def test_get_with_permit_no(test_client, db_session, auth_headers):
    permit_no = PermitFactory().permit_no

    get_resp = test_client.get(
        f'/permits?permit_no={permit_no}', headers=auth_headers['full_auth_header'])
    get_data = json.loads(get_resp.data.decode())
    assert get_resp.status_code == 200
    assert get_data.get('permit_no') == permit_no


#Create
def test_post_permit(test_client, db_session, auth_headers):
    mine = MineFactory()
    party_guid = PartyFactory(company=True).party_guid

    no_of_permits = len(mine.mine_permit)

    PERMIT_NO = 'mx-test-999'
    data = {
        'mine_guid': str(mine.mine_guid),
        'permittee_party_guid': str(party_guid),
        'permit_no': PERMIT_NO,
        'permit_status_code': 'O',
        'received_date': '1999-12-12',
        'issue_date': '1999-12-21',
        'authorization_end_date': '2012-12-02'
    }
    post_resp = test_client.post('/permits', headers=auth_headers['full_auth_header'], json=data)
    post_data = json.loads(post_resp.data.decode())

    updated_mine = Mine.find_by_mine_guid(str(mine.mine_guid))
    permittees = MinePartyAppointment.find_by_permit_guid(updated_mine.mine_permit[0].permit_guid)

    assert post_resp.status_code == 200
    assert updated_mine.mine_permit[0].permit_no == PERMIT_NO
    assert permittees[0].party_guid == party_guid
    assert len(updated_mine.mine_permit) == no_of_permits + 1


def test_post_permit_bad_mine_guid(test_client, db_session, auth_headers):
    data = {'mine_guid': str(uuid.uuid4())}
    post_resp = test_client.post('/permits', headers=auth_headers['full_auth_header'], json=data)
    assert post_resp.status_code == 404


def test_post_permit_with_duplicate_permit_no(test_client, db_session, auth_headers):
    mine_guid = MineFactory().mine_guid
    permit_no = PermitFactory().permit_no
    party_guid = PartyFactory(company=True).party_guid

    data = {
        'mine_guid': str(mine_guid),
        'permittee_party_guid': str(party_guid),
        'permit_no': permit_no
    }
    post_resp = test_client.post('/permits', headers=auth_headers['full_auth_header'], json=data)
    assert post_resp.status_code == 400


def test_post_with_permit_guid(test_client, db_session, auth_headers):
    mine_guid = MineFactory().mine_guid
    permit_guid = PermitFactory().permit_guid

    data = {
        'mine_guid': str(mine_guid),
        'permit_no': 'mx-test-999',
        'permit_status_code': 'O',
        'received_date': '1999-12-12',
        'issue_date': '1999-12-21',
        'authorization_end_date': '2012-12-02'
    }
    post_resp = test_client.post(
        f'/permits/{permit_guid}', headers=auth_headers['full_auth_header'], data=data)
    assert post_resp.status_code == 400


#Put
def test_put_permit(test_client, db_session, auth_headers):
    permit_guid = PermitFactory(permit_status_code='O').permit_guid

    data = {'permit_status_code': 'C'}
    put_resp = test_client.put(
        f'/permits/{permit_guid}', headers=auth_headers['full_auth_header'], json=data)
    put_data = json.loads(put_resp.data.decode())
    assert put_resp.status_code == 200
    assert put_data.get('permit_status_code') == 'C'


def test_put_permit_bad_permit_guid(test_client, db_session, auth_headers):
    PermitFactory(permit_status_code='O')

    data = {'permit_status_code': 'C'}
    put_resp = test_client.put(
        f'/permits/{uuid.uuid4()}', headers=auth_headers['full_auth_header'], json=data)
    assert put_resp.status_code == 404
