import sys
import json
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'fsnd-adrian.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'image'
token =  'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im9qYkNhNFhMcUJnVXoxdlNhWFU3ZCJ9.eyJpc3MiOiJodHRwczovL2ZzbmQtYWRyaWFuLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDExMjQ4MTc4NjI4NzM3NTY5NjE4NSIsImF1ZCI6ImltYWdlIiwiaWF0IjoxNjEzNTU0NzM5LCJleHAiOjE2MTM1NjE5MzksImF6cCI6InlaRk9RYWFyWkJsYmh2RGx2QXlDdGhuNHJ5b0xFWmUxIiwic2NvcGUiOiIifQ.mguXiKYTUXTAvUHb_AJDQKn0mz-i-qBdQDoZXF13fzerZRumbw7fn2bSAXMOt430M7qz_FN7v24XAUVsHjGu6YkGxP7X_38clr6d8E9jbFQjMrDUVZkOukLiknHSxHlLNeKN1EDxOEOKn6WqZtbhaUDmQ8trG2yh_zDg2p6SqqT81gDWDL5PrX810V6O3rII7vjxOXRJv4rNfsa2_m4Yslz4lppR0HGa_Yhjf4IPrBAaIOYFuSGIy3EESutJdYlhsmVbrtiKIN9JPhvI6W29nJ6Wbt_KTN8188HU6UeCvP8ihOrkOxNPdIhzwZGSKOOY8i9X0MMOkx23vtsvRJrxnA'

"""
https://fsnd-adrian.eu.auth0.com/authorize?
  audience=image&
  response_type=token&
  client_id=yZFOQaarZBlbhvDlvAyCthn4ryoLEZe1&
  redirect_uri=https://127.0.0.1:8080/login-results
"""

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header
def verify_decode_jwt(token):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    
    # GET THE DATA IN THE HEADER
    unverified_header = jwt.get_unverified_header(token)
    
    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    
    # Finally, verify!!!
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
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
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


print(verify_decode_jwt(token))