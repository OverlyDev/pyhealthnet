import datetime
from enum import IntEnum
from ipaddress import IPv4Address
from typing import Any, List, Literal
from uuid import NAMESPACE_DNS, UUID, uuid5

import orjson
from pydantic import BaseModel, HttpUrl, root_validator, validator


class Status(IntEnum):
    OK = 0
    ERROR = 1
    SHUTDOWN = 2
    RESTART = 3
    OTHER = 254


class Heartbeat(BaseModel):
    machine_id: UUID
    timestamp: datetime.datetime = datetime.datetime.utcnow()
    status: Status = Status.OK


class RegistrationRequest(BaseModel):
    client_name: str
    timestamp: datetime.datetime = datetime.datetime.utcnow()
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
    last_checkin: datetime.datetime = None
    interval: int = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.id = uuid5(self.network, self.name)


class Network(BaseModel):
    name: str = "pyhealthnet"
    id: UUID = None
    clients: List[Client] = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.id = uuid5(NAMESPACE_DNS, self.name)


if __name__ == "__main__":
    network = Network()
    print("network:\n", network.json)

    server = Server(hostname="phn.overly.dev", port=420)
    print("server:\n", server.json)

    client = Client(name="testclient", network=network.id)
    print("client:\n", client.json)

    rr = RegistrationRequest(client_name="testclient")
    print("rr:\n", rr.json)
    print()
    print(orjson.loads(rr.json()))
