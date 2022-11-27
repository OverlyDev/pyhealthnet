from fastapi import FastAPI, Response, status

from src.models.models import (
    Client,
    Heartbeat,
    RegistrationRequest,
    RegistrationResponse,
    Status,
)
from src.server.methods import CustomBackgroundHandler, create_network_from_env


network = create_network_from_env()
background = CustomBackgroundHandler()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


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
        reg_response = RegistrationResponse(machine_id=client.id)
        return reg_response
    else:
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
    background.refresh_task(client.interval, client_id)
    return
