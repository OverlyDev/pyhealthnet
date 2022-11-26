from src.models.models import RegistrationRequest, Server
from src.util.common import (
    CLIENT_NAME,
    MESSAGE_INTERVAL,
    SERVER_HOST,
    SERVER_HTTPS,
    SERVER_IP,
    SERVER_PORT,
    dict_to_tabbed_string,
    logger,
)


def create_server_from_env() -> Server:
    logger.info("Loading client settings from env")

    info = {
        "hostname": SERVER_HOST,
        "ip": SERVER_IP,
        "port": SERVER_PORT,
        "https": SERVER_HTTPS,
    }
    logger.debug("server info from env:")
    logger.debug(dict_to_tabbed_string(info))

    server = Server(**info)
    return server


def create_registration_request() -> RegistrationRequest:
    logger.info("Creating client registration request")

    info = {"client_name": CLIENT_NAME, "interval": MESSAGE_INTERVAL}
    logger.debug("client info:")
    logger.debug(dict_to_tabbed_string(info))

    reg_request = RegistrationRequest(**info)
    return reg_request


if __name__ == "__main__":
    create_server_from_env()
