import logging
import pathlib
from logging.config import dictConfig
from sys import stdout
from time import gmtime

from src.client.methods import (
    create_registration_request,
    create_server_from_env,
)
from src.models.models import RegistrationRequest
from src.util.common import (
    CLIENT_LOGGER,
    CLIENT_NAME,
    CLIENT_STORAGE,
    convert_model_to_json,
    generate_log_config,
)


# path setup
pathlib.Path.mkdir(CLIENT_STORAGE, exist_ok=True)

# set up logging
dictConfig(generate_log_config("client"))
logger = logging.getLogger("pyhealthnet-{}".format(CLIENT_LOGGER))


if __name__ == "__main__":
    logging.debug("Running in debug mode")
    server = create_server_from_env()
    rr = create_registration_request()
    print(convert_model_to_json(rr))
