import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

"""
https://fsnd-adrian.eu.auth0.com/authorize?
  audience=coffee-shop-api&
  response_type=token&
  client_id=Eg6UxTT62kSJvLywpvpogMouWJlgMjoq&
  redirect_uri=https://127.0.0.1:8080/login-results
"""

# Barista
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im9qYkNhNFhMcUJnVXoxdlNhWFU3ZCJ9.eyJpc3MiOiJodHRwczovL2ZzbmQtYWRyaWFuLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDMzYjJjMWI3NzFiMjAwNmI5Y2ZhMzMiLCJhdWQiOiJjb2ZmZWUtc2hvcC1hcGkiLCJpYXQiOjE2MTQzMzEwMDYsImV4cCI6MTYxNDMzODIwNiwiYXpwIjoiRWc2VXhUVDYya1NKdkx5d3B2cG9nTW91V0psZ01qb3EiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDpkcmlua3MtZGV0YWlsIl19.hUO8ITMSNuQhl76CkAuTsQSnmazMWdvkEdK4sb3Cz3EynXjXvf4s-iTZPZVx1XsAL7u9lLKbCTasX9hCKid89l0iJxVAo6Jbt5fR3GQTLFVkG2Udm1pWFgIsqWG89cZucRU-onqdo7WC4oC7lSNZghphEdj9B3Ki0EPTfRTkNpaMSe4unGA5k-GPgooCDwVCjhx4k0Df8VNy99l2eyvUq1am7NEom1pd9S79i3AsuIpdvBUNBsSXC_4BlDbRkTWHuFKL87fIck04A8FmpuATqWXGfQ_eQzULCC-qllNGD0RXSZEr6njcOLNVsN4qIeDU1BtPUzRqm4mpAE5EG6DAjw

# Manager
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im9qYkNhNFhMcUJnVXoxdlNhWFU3ZCJ9.eyJpc3MiOiJodHRwczovL2ZzbmQtYWRyaWFuLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDMzYjJlNzE1ZGYzMzAwNzE0YmU5MWQiLCJhdWQiOiJjb2ZmZWUtc2hvcC1hcGkiLCJpYXQiOjE2MTQzMzA5NDQsImV4cCI6MTYxNDMzODE0NCwiYXpwIjoiRWc2VXhUVDYya1NKdkx5d3B2cG9nTW91V0psZ01qb3EiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTpkcmlua3MiLCJnZXQ6ZHJpbmtzLWRldGFpbCIsInBhdGNoOmRyaW5rcyIsInBvc3Q6ZHJpbmtzIl19.PasXDGcB229Bh83uUsu7S3foGxCcrvk3sc345A4y3RU783hWjQ-0bAKdGnqaMbqO75q3iEewPMZP0EIrjBd-16EeUJlIXbgl8iEnmmiCKAFFZlef07ely0iEoufcUFnWk3X2GH4jLOjEXwrD_w4almI0mj7cdu8ey7j_syweu5q7mREUtLaP-IOyEiP4p3ysMYbwiFzqh26C7VnUjfvCIoBFZ3NeCXq0qrzLKdbuD1cXAnAHsj7Sb553pUIDMcZaSV-BIxKpNNLpuKhx-fGQ1vUUaU1_gu0aQj_Qv6HjIbtpZrZEZGzhSOX7yxGUvZPeYgZW4LqLyFqVzv8TueLC4w


AUTH0_DOMAIN = 'fsnd-adrian.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee-shop-api'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO DONE implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token

'''
@TODO DONE implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)
    
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    
    return True

'''
@TODO DONE implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    unverified_header = jwt.get_unverified_header(token)
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)
    
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    rsa_key = {}

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception as e:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


'''
@TODO DONE implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator