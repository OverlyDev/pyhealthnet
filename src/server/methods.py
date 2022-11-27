import asyncio
import logging

from src.models.models import FastApiConfig, Network
from src.util.common import (
    API_DOCS,
    GRACE_PERIOD,
    NETWORK_NAME,
    SERVER_LOGGER,
    convert_model_to_json,
)


# set up logging for this module
logger = logging.getLogger("pyhealthnet-{}".format(SERVER_LOGGER))


def generate_fastapi_config() -> dict:
    return FastApiConfig(docs_enabled=API_DOCS).dict()


def create_network_from_env() -> Network:

    info = {"name": NETWORK_NAME}
    network = Network(**info)
    logger.debug("Created network from env:")
    logger.debug(convert_model_to_json(network))

    return network


async def expect_client_response(duration: int, client_id):
    try:
        logger.debug("Client ({}), sleeping for {}s".format(client_id, duration))
        await asyncio.sleep(duration)

        logger.debug(
            "Client ({}), sleeping for grace period: {}s".format(
                client_id, GRACE_PERIOD
            )
        )
        await asyncio.sleep(GRACE_PERIOD)

        logger.debug("Client ({}), triggering notification".format(client_id))
        send_notification(client_id)
        return

    except asyncio.CancelledError:
        logger.debug("Client ({}), received cancel".format(client_id))
        return


def send_notification(client_id):
    logger.error("Client ({}), OH MY GOD NOTIFICATION".format(client_id))
    return


class ServerBackgroundHandler:
    def __init__(self) -> None:
        self.tasks = {}

    def add_sleep_task(self, duration: int, client_id):
        # create the task
        task = asyncio.create_task(
            expect_client_response(duration, client_id), name=client_id
        )
        self.tasks.update({client_id: task})

    def cancel_sleep_task(self, client_id):
        task = self.tasks.get(client_id)
        if task is not None:
            task.cancel()

    def refresh_task(self, duration: int, client_id):
        self.cancel_sleep_task(client_id)
        self.add_sleep_task(duration, client_id)
