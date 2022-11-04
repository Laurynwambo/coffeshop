import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen

from src.settings import AUTH0_DOMAIN, API_AUDIENCE, ALGORITHMS
## AuthError Exception
"""
AuthError Exception
A standardized way to communicate auth failure modes
"""


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header
def get_token_auth_header():

    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError(
            {
                "description": "Expected Header Authorization .",
                "code": "authorization_header_missing",
               
                
            },
            401,
        )

    parts = auth.split()
    if len(parts) == 1:
        raise AuthError(
            {"code": "missing_token", "description": "Missing token."}, 404
        )

    elif parts[0].lower() != "bearer":
        raise AuthError(
            {
                "code": "invalid_header",
                "description": 'Start Authorization Header with a bearer.',
            },
            404,
        )

    
    elif len(parts) > 2:
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization header must be bearer token.",
            },
            404,
        )

    token = parts[1]
    return token


def check_permissions(permission, payload):
    if permission not in payload["permissions"]:
        raise AuthError(
            {"code": "unauthorized", "description": "Not Authorized."}, 405
        )
    if "permissions" not in payload:
        raise AuthError(
            {
                "code": "Not authhorized",
                "description": "JWT missing required permissions.",
            },
            405,
        )

    
    return True


def verify_decode_jwt(token):
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())

    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    if "kid" not in unverified_header:
        raise AuthError(
            {"code": "invalid_header", "description": "Authorization malformed."}, 401
        )

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kid": key["kid"],
                "kty": key["kty"],
                "e": key["e"],
                "use": key["use"],
                "n": key["n"],
                
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://" + AUTH0_DOMAIN + "/",
            )

            return payload

        except jwt.JWTClaimsError:
            raise AuthError(
                {
                    "code": "invalid_requests",
                    "description": "Invalid requests, please get the correct token.",
                },
                405,
            )

        except Exception:
            raise AuthError(
                {
                    "code": "invalid_token",
                    "description": "Cannot render provided token.",
                },
                405,
            )

        except jwt.ExpiredSignatureError:
            raise AuthError(
                {"code": "token_expired", "description": "Token expired."}, 405
            )

       
        
    raise AuthError(
        {
            "code": "invalid_header",
            "description": "Cannot find key.",
        },
        405,
    )



def requires_auth(permission=""):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
           
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator