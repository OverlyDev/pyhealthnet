import logging
import pathlib
from logging import Formatter
from os import getenv
from time import gmtime
from typing import Any, Literal

import orjson
from dotenv import load_dotenv
from pydantic import BaseModel


logger = logging.getLogger()

# load things from ENV
load_dotenv()
DEBUG_LOGS = bool(True if getenv("DEBUG_LOGS").lower() == "true" else False)

# client env
CLIENT_LOGGER = getenv("CLIENT_LOGGER")
SERVER_HOST = getenv("SERVER_HOST")
SERVER_IP = getenv("SERVER_IP")
SERVER_PORT = getenv("SERVER_PORT")
SERVER_HTTPS = getenv("SERVER_HTTPS")
MESSAGE_INTERVAL = getenv("MESSAGE_INTERVAL")
CLIENT_NAME = getenv("CLIENT_NAME")

# server env
SERVER_LOGGER = getenv("SERVER_LOGGER")
NETWORK_NAME = getenv("NETWORK_NAME")
GRACE_PERIOD = int(getenv("GRACE_PERIOD"))
API_DOCS = bool(True if getenv("API_DOCS").lower() == "true" else False)

# storage folders
CWD = pathlib.Path(__file__).parent.resolve()
CLIENT_PATH = CWD.parent / "client"
CLIENT_STORAGE = CLIENT_PATH / "client-storage"
SERVER_PATH = CWD.parent / "server"
SERVER_STORAGE = SERVER_PATH / "server-storage"


class UTCFormatter(Formatter):
    converter = gmtime


class LogConfig(BaseModel):
    """Logging configuration for pyHealthNet"""

    LOGGER_NAME: str = "pyhealthnet"
    LOG_FORMAT: str = "[%(asctime)s] %(levelname)-8s %(module)-12s %(message)s"
    LOG_LEVEL: str = "INFO"
    version: int = None
    disable_existing_loggers: bool = None
    formatters: dict = None
    handlers: dict = None
    loggers: dict = None

    def __init__(self, suffix: str, **data: Any) -> None:
        super().__init__(**data)

        self.LOGGER_NAME += "-{}".format(suffix)

        self.version = 1
        self.disable_existing_loggers = False
        self.formatters = {
            "default": {
                "()": UTCFormatter,
                "fmt": self.LOG_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        }
        self.handlers = {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        }
        self.loggers = {
            self.LOGGER_NAME: {"handlers": ["default"], "level": self.LOG_LEVEL},
        }


def generate_log_config(client_or_server: Literal["client", "server"]) -> dict:
    level = "DEBUG" if DEBUG_LOGS else "INFO"
    if client_or_server == "client":
        suffix = CLIENT_LOGGER
    elif client_or_server == "server":
        suffix = SERVER_LOGGER
    else:
        print("Something bad happened in: src.util.common.generate_log_config")
        exit(1)
    config = LogConfig(suffix, LOG_LEVEL=level)
    return config.dict()


def dict_to_tabbed_string(dictionary: dict) -> str:
    string = ""
    for k, v in dictionary.items():
        string += "\t{}: {}".format(k, v)
    return string


def convert_model_to_json(model: BaseModel):
    return orjson.loads(model.json())
