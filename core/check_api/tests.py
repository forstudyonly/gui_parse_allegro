import base64
import hashlib
import os
import secrets
import string
import requests
from dotenv import load_dotenv
import json

load_dotenv()


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

REDIRECT_URI = "http://localhost:8000"

TOKEN_URL = "https://allegro.pl/auth/oauth/token"
AUTH_URL = "https://allegro.pl/auth/oauth/authorize"


def generate_code_verifier():
    code_verifier = ''.join((secrets.choice(string.ascii_letters) for i in range(40)))
    return code_verifier


def get_access_token(authorization_code, code_verifier):
    try:
        data = {'grant_type': 'authorization_code', 'code': authorization_code,
                'redirect_uri': REDIRECT_URI, 'code_verifier': code_verifier}
        access_token_response = requests.post(TOKEN_URL, data=data, verify=False,
                                              allow_redirects=False)
        print(access_token_response.text)
        response_body = json.loads(access_token_response.text)
        return response_body
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


def generate_code_challenge(code_verifier):
    hashed = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    base64_encoded = base64.urlsafe_b64encode(hashed).decode('utf-8')
    code_challenge = base64_encoded.replace('=', '')
    return code_challenge


def check_token(access_token):
    environment = "allegro.pl"
    url = f"https://api.{environment}/sale/offers"
    headers = {
        "authorization": f"Bearer {access_token}",
        "accept": "application/vnd.allegro.public.v1+json"
    }
    response = requests.get(url=url, headers=headers)
    print(response.text)
    return response.status_code


def get_link():
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    authorization_redirect_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}" \
                                 f"&code_challenge_method=S256&code_challenge={code_challenge}"
    return authorization_redirect_url, code_verifier


def get_access_token(authorization_code, code_verifier):
    try:
        data = {'grant_type': 'authorization_code', 'code': authorization_code,
                'redirect_uri': REDIRECT_URI, 'code_verifier': code_verifier}
        access_token_response = requests.post(TOKEN_URL, data=data, verify=False,
                                              allow_redirects=False)
        print(access_token_response.text)
        response_body = json.loads(access_token_response.text)
        return response_body
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)



