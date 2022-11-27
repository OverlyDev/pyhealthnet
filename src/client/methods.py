import asyncio
import logging
import signal

from src.models.models import RegistrationRequest, Server
from src.util.common import (
    CLIENT_LOGGER,
    CLIENT_NAME,
    MESSAGE_INTERVAL,
    SERVER_HOST,
    SERVER_HTTPS,
    SERVER_IP,
    SERVER_PORT,
    dict_to_tabbed_string,
)


# set up logging for this module
logger = logging.getLogger("pyhealthnet-{}".format(CLIENT_LOGGER))


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


async def looping_task(task_num):
    try:
        while True:
            logging.info("{0}:in looping_task".format(task_num))
            await asyncio.sleep(5.0)
    except asyncio.CancelledError:
        return "{0}: I was cancelled!".format(task_num)


class ClientBackgroundHandler:
    def __init__(self) -> None:
        self.loop = asyncio.get_running_loop()

    def add_task(self, func, *args, **kwargs):
        asyncio.ensure_future(func(*args, **kwargs), loop=self.loop)

    def _add_signal_handlers(self):
        async def shutdown(sig: signal.Signals) -> None:
            """
            Cancel all running async tasks (other than this one) when called.
            By catching asyncio.CancelledError, any running task can perform
            any necessary cleanup when it's cancelled.
            """
            tasks = []
            for task in asyncio.all_tasks(self.loop):
                if task is not asyncio.current_task(self.loop):
                    task.cancel()
                    tasks.append(task)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            print("Finished awaiting cancelled tasks, results: {0}".format(results))
            self.loop.stop()

        for sig in [signal.SIGINT, signal.SIGTERM]:
            self.loop.add_signal_handler(
                sig, lambda: asyncio.create_task(shutdown(sig))
            )

    def run(self):
        self._add_signal_handlers()
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()
