import requests
import json
import dotenv
import jwt
import base64

from dotenv import load_dotenv, find_dotenv


def keycloak_test():
    ENV_FILE = find_dotenv(filename='python-backend/.env')
    if ENV_FILE:
        load_dotenv(ENV_FILE)

    username = 'pdittaro'
    password = 'test'
    client_id = 'mines-application-local'
    client_secret = '**********'
    resource_name = 'Super Resource'

    # print('Getting Access Token')
    # access_token_payload = oidc_connect(
    #     username, password, client_id, client_secret)

    # print('Getting permissions')
    # rpt = get_rpt_token(access_token_payload, client_id)
    # decoded_rpt = decode_token(rpt)
    # print(decoded_rpt['access_token']['authorization']['permissions'])

    # print('Asking permission')
    # rpt = ask_permission(access_token_payload, client_id, "Default Resource")
    # print(rpt)

    print('Logging on as Resource Server?')
    pat = get_pat(client_id, client_secret)
    # print(pat)

    print('Get all resources')
    resources = get_resources(pat)
    print(resources)
    for resource in resources:
        get_resource(pat, resource)
    print('Create Resource')
    # create_resource(pat, resource_name)

    # get_resources(pat)


def oidc_connect(username, password, client_id, client_secret):
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'password', 'client_id': client_id, 'client_secret': client_secret,
            'username': username, 'password': password}
    response = requests.post(
        'http://localhost:8080/auth/realms/mds/protocol/openid-connect/token', headers=headers, data=data)
    access_token = response.json()
    return access_token


def get_rpt_token(access_token_payload, client_id):
    headers = {
        'Authorization': f"Bearer {access_token_payload['access_token']}"}
    data = {'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
            'audience': client_id}
    response = requests.post(
        'http://localhost:8080/auth/realms/mds/protocol/openid-connect/token', headers=headers, data=data)
    rpt = response.json()
    return rpt


def ask_permission(access_token_payload, client_id, resource_name):
    headers = {
        'Authorization': f"Bearer {access_token_payload['access_token']}"}
    data = {'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
            'audience': client_id,
            'response_mode': 'decision',
            'permission': f'{resource_name}'}
    response = requests.post(
        'http://localhost:8080/auth/realms/mds/protocol/openid-connect/token', headers=headers, data=data)
    rpt = response.json()
    return rpt


def get_pat(client_id, client_secret):
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'client_credentials',
            'client_id': client_id, 'client_secret': client_secret}
    response = requests.post(
        'http://localhost:8080/auth/realms/mds/protocol/openid-connect/token', headers=headers, data=data)
    pat = response.json()
    return pat


def get_resources(pat):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {pat['access_token']}"
    }
    response = requests.get(
        'http://localhost:8080/auth/realms/mds/authz/protection/resource_set', headers=headers)

    return response.json()


def get_resource(pat, id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {pat['access_token']}"}
    response = requests.get(
        f'http://localhost:8080/auth/realms/mds/authz/protection/resource_set/{id}', headers=headers)
    print(response.json())


def create_resource(pat, resource_name):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {pat['access_token']}"}

    data = {'name': 'Super cool resource',
            'ownerManagedAccess': False,
            'displayName': 'Test Resource, PROGRAMMATICALLY created',
            'attributes': {},
            'uris': [],
            'resource_scopes': []}

    data_str = json.dumps(data)

    response = requests.post(
        'http://localhost:8080/auth/realms/mds/authz/protection/resource_set', headers=headers, data=data_str)
    print(response)


def decode_token(t):
    t['access_token'] = jwt.decode(t['access_token'], verify=False)
    t['refresh_token'] = jwt.decode(t['refresh_token'], verify=False)
    return t


keycloak_test()
