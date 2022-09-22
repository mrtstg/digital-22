from jwt import api_jwt as jwt
from jwt import InvalidTokenError, ExpiredSignatureError
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials
from starlette.exceptions import HTTPException

from auth.jwt_user import JWTUser


class JWTAuthenticationBackend(AuthenticationBackend):
    def __init__(self, secret_key: str, algorithm: str = "HS256", prefix: str = "Bearer"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.prefix = prefix

    @classmethod
    def get_token_from_cookie(cls, authorization: str, prefix: str):
        print(f"JWT token from headers: {authorization}", "cyan")  # debug part, do not forget to remove it
        try:
            scheme, token = authorization.split()
        except ValueError:
            print(f"Could not separate Authorization scheme and token", "red")
            raise AuthenticationError("Could not separate Authorization scheme and token")
        if scheme.lower() != prefix.lower():
            print(f"Authorization scheme {scheme} is not supported", "red")
            raise AuthenticationError(f"Authorization scheme {scheme} is not supported")
        return token

    async def authenticate(self, request):
        if "token" not in request.cookies:
            return None
        authorization = request.cookies['token']
        token = self.get_token_from_cookie(authorization=authorization, prefix=self.prefix)

        try:
            jwt_payload = jwt.decode(token, key=str(self.secret_key), algorithms=self.algorithm)
        except ExpiredSignatureError:
            raise AuthenticationError("Expired JWT token")
        except InvalidTokenError:
            raise AuthenticationError("Invalid JWT token")

        print(f"Decoded JWT payload: {jwt_payload}", "green")  # debug part, do not forget to remove it

        return (
            AuthCredentials(["authenticated"]),
            JWTUser(username=jwt_payload["username"], user_id=jwt_payload["user_id"], token=token),
        )
