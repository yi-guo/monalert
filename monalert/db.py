from typing import Final, List

import os
import pymongo

ENV_MONGO_HOST: Final[str] = "MONGO_HOST"
ENV_MONGO_PORT: Final[str] = "MONGO_PORT"
ENV_MONGO_INITDB_ROOT_USERNAME: Final[str] = "MONGO_INITDB_ROOT_USERNAME"
ENV_MONGO_INITDB_ROOT_PASSWORD: Final[str] = "MONGO_INITDB_ROOT_PASSWORD"

MONGO_DATABASE: Final[str] = "monalert"


def get_mongo_database() -> pymongo.database.Database:
    envs: List[str] = [
        ENV_MONGO_HOST,
        ENV_MONGO_PORT,
        ENV_MONGO_INITDB_ROOT_USERNAME,
        ENV_MONGO_INITDB_ROOT_PASSWORD,
    ]
    for env in envs:
        if not os.getenv(env):
            raise RuntimeError(f"Missing environment variable {env}")
    host: str = os.environ[ENV_MONGO_HOST]
    port: int = int(os.environ[ENV_MONGO_PORT])
    username: str = os.environ[ENV_MONGO_INITDB_ROOT_USERNAME]
    password: str = os.environ[ENV_MONGO_INITDB_ROOT_PASSWORD]
    return pymongo.MongoClient(
        f"mongodb://{username}:{password}@{host}:{port}")[MONGO_DATABASE]
