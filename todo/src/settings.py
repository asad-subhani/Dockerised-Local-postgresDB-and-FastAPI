from starlette.config import Config
from starlette.datastructures import Secret


config = Config(".env")
DB_URL = config("DB_URL", cast=str)