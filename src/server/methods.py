import asyncio

from src.models.models import Network
from src.util.common import GRACE_PERIOD, NETWORK_NAME, logger


def create_network_from_env() -> Network:
    logger.info("Creating network from env")

    info = {"name": NETWORK_NAME}
    network = Network(**info)
    return network


async def expect_client_response(duration: int, client_id):
    try:
        print("sleeping for client interval:", duration)
        await asyncio.sleep(duration)
        print("sleeping for grace period:", GRACE_PERIOD)
        await asyncio.sleep(GRACE_PERIOD)
        print("triggering notification")
        send_notification(client_id)
        return

    except asyncio.CancelledError:
        print("received cancel for:", client_id)
        return


def send_notification(client_id):
    print("OH MY GOD NOTIFICATION BECAUSE OF:", client_id)
    return


class CustomBackgroundHandler:
    def __init__(self) -> None:
        self.tasks = {}

    def add_sleep_task(self, duration: int, client_id):
        # create the task
        task = asyncio.create_task(
            expect_client_response(duration, client_id), name=client_id
        )
        self.tasks.update({client_id: task})

    def cancel_sleep_task(self, client_id):
        print("Cancelling task")
        task = self.tasks.get(client_id)
        if task is not None:
            task.cancel()

    def refresh_task(self, duration: int, client_id):
        self.cancel_sleep_task(client_id)
        self.add_sleep_task(duration, client_id)
