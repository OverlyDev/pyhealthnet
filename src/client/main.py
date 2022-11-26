import asyncio
import logging
import pathlib
import signal
from sys import stdout
from time import gmtime

from src.client.methods import (
    create_registration_request,
    create_server_from_env,
)
from src.models.models import RegistrationRequest
from src.util.common import (
    CLIENT_NAME,
    CLIENT_STORAGE,
    DEBUG_LOGS,
    convert_model_to_json,
    logger,
)


# path setup
pathlib.Path.mkdir(CLIENT_STORAGE, exist_ok=True)

# logging setup
logging.Formatter.converter = gmtime
formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s %(module)-12s %(message)s")

if DEBUG_LOGS:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler(stdout)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


async def looping_task(task_num):
    try:
        while True:
            logging.info("{0}:in looping_task".format(task_num))
            await asyncio.sleep(5.0)
    except asyncio.CancelledError:
        return "{0}: I was cancelled!".format(task_num)


def add_signal_handlers():
    loop = asyncio.get_event_loop()

    async def shutdown(sig: signal.Signals) -> None:
        """
        Cancel all running async tasks (other than this one) when called.
        By catching asyncio.CancelledError, any running task can perform
        any necessary cleanup when it's cancelled.
        """
        tasks = []
        for task in asyncio.all_tasks(loop):
            if task is not asyncio.current_task(loop):
                task.cancel()
                tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print("Finished awaiting cancelled tasks, results: {0}".format(results))
        loop.stop()

    for sig in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(sig)))


def main():
    loop = asyncio.get_event_loop()
    for i in range(5):
        asyncio.ensure_future(looping_task(i), loop=loop)
    add_signal_handlers()

    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == "__main__":
    logging.debug("Running in debug mode")
    server = create_server_from_env()
    rr = create_registration_request()
    print(convert_model_to_json(rr))
