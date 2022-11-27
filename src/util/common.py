import logging
import pathlib
from os import getenv

import orjson
from dotenv import load_dotenv
from pydantic import BaseModel


logger = logging.getLogger()

# load things from ENV
load_dotenv()
DEBUG_LOGS = bool(True if getenv("DEBUG_LOGS").lower() == "true" else False)

# client env
SERVER_HOST = getenv("SERVER_HOST")
SERVER_IP = getenv("SERVER_IP")
SERVER_PORT = getenv("SERVER_PORT")
SERVER_HTTPS = getenv("SERVER_HTTPS")
MESSAGE_INTERVAL = getenv("MESSAGE_INTERVAL")
CLIENT_NAME = getenv("CLIENT_NAME")

# server env
NETWORK_NAME = getenv("NETWORK_NAME")
GRACE_PERIOD = int(getenv("GRACE_PERIOD"))
API_DOCS = bool(True if getenv("API_DOCS").lower() == "true" else False)

# storage folders
CWD = pathlib.Path(__file__).parent.resolve()
CLIENT_PATH = CWD.parent / "client"
CLIENT_STORAGE = CLIENT_PATH / "client-storage"
SERVER_PATH = CWD.parent / "server"
SERVER_STORAGE = SERVER_PATH / "server-storage"


def dict_to_tabbed_string(dictionary: dict) -> str:
    string = ""
    for k, v in dictionary.items():
        string += "\t{}: {}".format(k, v)
    return string


def convert_model_to_json(model: BaseModel):
    return orjson.loads(model.json())
