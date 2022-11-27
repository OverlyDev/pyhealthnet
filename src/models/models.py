import datetime
from enum import IntEnum
from ipaddress import IPv4Address
from typing import Any, Dict, List
from uuid import NAMESPACE_DNS, UUID, uuid5

import orjson
from pydantic import BaseModel, HttpUrl, root_validator, validator


class Status(IntEnum):
    OK = 0
    ERROR = 1
    SHUTDOWN = 2
    RESTART = 3
    REGISTERED = 250
    OTHER = 254


class Heartbeat(BaseModel):
    machine_id: UUID
    status: Status = Status.OK


class RegistrationRequest(BaseModel):
    client_name: str
    interval: int = 60 * 5  # 5 minutes


class RegistrationResponse(BaseModel):
    machine_id: UUID


class Server(BaseModel):
    hostname: str = None
    ip: IPv4Address = None
    port: int
    https: bool = False
    url: HttpUrl = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if self.hostname is None:
            host = self.ip
        else:
            host = self.hostname

        prefix = "https://" if self.https else "http://"
        self.url = prefix + str(host) + ":" + str(self.port)

    @root_validator(pre=True)
    def hostname_or_port_assigned(cls, values):
        host = values.get("hostname")
        ip = values.get("ip")
        if (host is None) and (ip is None):
            raise ValueError("Hostname or ip must be set")
        return values

    @validator("port")
    def valid_port(cls, value):
        if not 1 <= value <= 65535:
            raise ValueError("Invalid port value")
        return value


class Client(BaseModel):
    name: str
    network: UUID
    id: UUID = None
    last_checkin: datetime.datetime = datetime.datetime.utcnow()
    interval: int = None
    last_status: Status = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.id = uuid5(self.network, self.name)


class Network(BaseModel):
    name: str = "pyhealthnet"
    id: UUID = None
    clients: Dict[UUID, Client] = {}

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.id = uuid5(NAMESPACE_DNS, self.name)

    def add_client(self, client: Client) -> bool:
        if client.id in self.clients.keys():
            return False
        self.clients.update({client.id: client})
        return True

    def get_client(self, client_id) -> Client:
        return self.clients[client_id]

    def get_client_ids(self) -> List[UUID]:
        return self.clients.keys()

    def client_heartbeat(self, heartbeat: Heartbeat):
        client_id = heartbeat.machine_id
        client = self.clients.get(client_id)
        client.last_checkin = datetime.datetime.utcnow()
        client.last_status = heartbeat.status
        self.clients[client_id] = client


class ServerLogConfig(BaseModel):
    """Logging configuration for the pyHealthNet server"""

    LOGGER_NAME: str = "pyhealthnet-server"
    LOG_FORMAT: str = "[%(asctime)s] %(levelname)-8s %(module)-12s %(message)s"
    LOG_LEVEL: str = "INFO"
    version: int = None
    disable_existing_loggers: bool = None
    formatters: dict = None
    handlers: dict = None
    loggers: dict = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

        # logging config
        self.version = 1
        self.disable_existing_loggers = False
        self.formatters = {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
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
            "pyhealthnet-server": {"handlers": ["default"], "level": self.LOG_LEVEL},
        }


class FastApiConfig(BaseModel):
    docs_enabled: bool
    title: str = "pyHealthNet Server"
    description: str = None
    version: str = "0.0.1"
    terms_of_service: str = ""
    contact = {
        "name": "OverlyDev",
        "url": None,
        "email": None,
    }
    # license_info = {
    #     "name": "",
    #     "url": "",
    # }
    openapi_url: str = "/api/v1/openapi.json"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if not self.docs_enabled:
            self.openapi_url = None
            self.docs_url = None
            self.redoc_url = None
