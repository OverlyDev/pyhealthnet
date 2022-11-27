import logging
from logging.config import dictConfig

from fastapi import FastAPI, Response, status

from src.models.models import (
    Client,
    Heartbeat,
    RegistrationRequest,
    RegistrationResponse,
    Status,
)
from src.server.methods import (
    CustomBackgroundHandler,
    create_network_from_env,
    generate_fastapi_config,
    generate_log_config,
)


# set up logging
dictConfig(generate_log_config())
logger = logging.getLogger("pyhealthnet-server")

network = create_network_from_env()
background = CustomBackgroundHandler()

app = FastAPI(**generate_fastapi_config())


@app.get("/")
async def root():
    return {"detail": "pyHealthNet Server"}


@app.post("/register")
async def register(
    reg_request: RegistrationRequest, response: Response
) -> RegistrationResponse:
    client_info = {
        "name": reg_request.client_name,
        "network": network.id,
        "interval": reg_request.interval,
        "last_status": Status.REGISTERED,
    }
    client = Client(**client_info)
    if network.add_client(client):
        logger.info("Registered client: {}".format(client.id))
        reg_response = RegistrationResponse(machine_id=client.id)
        return reg_response
    else:
        logger.info("Client already registered: {}".format(client.id))
        response.status_code = status.HTTP_418_IM_A_TEAPOT
        return


@app.post("/heartbeat")
async def heartbeat(data: Heartbeat, response: Response):
    client_id = data.machine_id
    if client_id not in network.get_client_ids():
        response.status_code = status.HTTP_418_IM_A_TEAPOT
        return

    network.client_heartbeat(data)
    client = network.get_client(client_id)

    if client.last_status == Status.OK:
        logger.info(
            "Client ({}), last status: {} (OK), waiting for next heartbeat".format(
                client_id, client.last_status
            )
        )
        background.refresh_task(client.interval, client_id)

    else:
        logger.info(
            "Client ({}), last status: {} (Not OK), not waiting for next heartbeat".format(
                client_id, client.last_status
            )
        )
        background.cancel_sleep_task(client_id)

    return
