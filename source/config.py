from starlette.config import Config
from starlette.datastructures import Secret

config = Config('.env')

POSTGRES_USER = config('POSTGRES_USER', cast=str)
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD', cast=str)
POSTGRES_HOST = config('POSTGRES_HOST', cast=str)
POSTGRES_PORT = config('POSTGRES_PORT', cast=str)
POSTGRES_DATABASE = config('POSTGRES_DATABASE', cast=str)

DATABASE_URL = "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE
)

DATABASE_URL_SYNC = "postgresql://{}:{}@{}:{}/{}".format(
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE
)

SECRET_KEY = config("SECRET_KEY", cast=Secret)
# ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=CommaSeparatedStrings)
JWT_PREFIX = config("JWT_PREFIX", cast=str)
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str)
