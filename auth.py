from functools import wraps
import json
import secrets
import string
from urllib.request import urlopen

from flask import request, _request_ctx_stack
from jose import jwt

from config import AUTH0_DOMAIN, API_AUDIENCE

AUTH0_DOMAIN = AUTH0_DOMAIN
ALGORITHMS = ['RS256']
API_AUDIENCE = API_AUDIENCE


# AuthError Exception
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
def get_token_auth_header():
    header = request.headers.get('Authorization')
    if header is None:
        raise AuthError('Missing auth header', 401)
    token = header.split(' ')
    if len(token) != 2 or token[0] != 'Bearer' or token[1] is None:
        raise AuthError('Malformed auth header', 401)
    return token[1]


def check_permissions(permission, payload):
    permissions = payload.get('permissions')
    if permissions is None:
        raise AuthError(
            'Invalid auth token. Unable to locate permission scopes.', 401
        )
    if permission and permission not in permissions:
        raise AuthError(
            'Invalid permission scope. User has insufficient privileges.', 401
        )


def verify_decode_jwt(token):
    # Get the public key from Auth0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # Get the data in the header
    unverified_header = jwt.get_unverified_header(token)

    # Choose the key
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError('Invalid auth header', 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    # Verify
    if rsa_key:
        try:
            # Use the key to validate the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError('Expired auth token', 401)
        except jwt.JWTClaimsError:
            raise AuthError(
                'Invalid auth claim. Check the audience and issuer.', 403
            )
        except Exception:
            raise AuthError(
                'Invalid auth header. Unable to parse auth token.', 400
            )
    raise AuthError(
        'Invalid auth header. Unable to find the appropriate key.', 400
    )


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except AuthError:
                raise
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator


def generate_random_string_with_digits(length=6):
    """Generate a random string of letters and digits"""
    letters_and_digits = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(letters_and_digits) for i in range(length))
