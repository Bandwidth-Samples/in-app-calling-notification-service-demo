import asyncio
import json
import logging
import os

from bandwidth.models import InitiateCallback, DisconnectCallback, RedirectCallback
from bandwidth.models.bxml import Response as BxmlResponse
from bandwidth.models.bxml import Bridge, SpeakSentence, Ring, Redirect
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
import redis
import requests
from starlette.middleware.cors import CORSMiddleware
import threading
import uvicorn

logger = logging.getLogger('uvicorn.error')
logging.basicConfig(level=logging.DEBUG)

try:
    BW_USERNAME = os.environ.get("BW_USERNAME")
    BW_PASSWORD = os.environ.get("BW_PASSWORD")
    IN_APP_CALLING_NUMBER = os.environ.get("BW_FROM_NUMBER")
except KeyError as e:
    logger.error(f"Missing environment variable: {e}. Did you set up your .env file?")
    exit(1)

connected_clients = []

app = FastAPI()

# CORS Middleware for our Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

async def handle_message(message):
    logger.debug(f"Redis message received: {message['data']}")
    for client in connected_clients:
        try:
            await client.send_text(message['data'])
            logger.debug(f"Message sent to client: {message['data']}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

def redis_listener():
    logger.debug("Starting Redis listener")
    pubsub = redis_client.pubsub()
    pubsub.subscribe("calls")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for message in pubsub.listen():
        if message['type'] == 'message':
            loop.run_until_complete(handle_message(message))

def start_redis_listener():
    listener_thread = threading.Thread(target=redis_listener, daemon=True)
    listener_thread.start()


@app.get("/health", status_code=204)
def health_check() -> None:
    """
    Health check endpoint
    :return: None
    """
    return

@app.get(path="/bandwidth/authorization/token", status_code=200)
def get_bandwidth_token() -> Response:
    """
    Get Bandwidth JWT from the Oauth Endpoint
    :return: str
    """
    logger.info("Fetching Bandwidth Token")
    bandwidth_token_url = "https://id.bandwidth.com/api/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    payload = {
        "grant_type": "client_credentials"
    }
    r = requests.post(bandwidth_token_url, auth=(BW_USERNAME, BW_PASSWORD), headers=headers, data=payload)
    token = r.json()["access_token"]

    # return token with quotes removed
    return Response(content=token.replace('"', ""), headers={"Content-Type": "text/plain"})


@app.websocket("/bandwidth/notifications/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        connected_clients.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connected_clients.remove(websocket)
        await websocket.close()


@app.post("/bandwidth/notifications/notify")
async def notify_user(message: dict):
    await redis_client.publish("incoming-calls", message)
    return {"status": "message sent"}


@app.post("/bandwidth/webhooks/voice/disconnect")
def handle_disconnect(callback: DisconnectCallback):
    logger.info(f"Received disconnect for call {callback.call_id}")
    logger.debug(callback)
    return


@app.post("/bandwidth/webhooks/voice/initiate")
def handle_inbound_call(callback: InitiateCallback):
    logger.info(f"Received inbound call from {callback.var_from}")
    logger.debug(callback)

    if callback.var_from == IN_APP_CALLING_NUMBER:
        logger.info("Received call from our agent to bridge")
        # Call from our agent - we need to bridge this to an inbound customer call
        customer_call_id = redis_client.get("inbound_call_id")
        bridge = Bridge(target_call=customer_call_id)
        response = BxmlResponse([bridge])
        return Response(status_code=200, content=response.to_bxml(), media_type="application/xml")
    else:
        logger.info("Received call from a customer")
        redis_client.set("inbound_call_id", callback.call_id)
        message = {
            "type": "call",
            "data": {
                "fromNumber": callback.var_from,
                "callId": callback.call_id
            }
        }
        redis_client.publish("calls", json.dumps(message))

        speak_sentence = SpeakSentence(
            text="Thank you for calling Bandwidth. Please wait while we connect you to an agent."
        )
        ring = Ring(
            duration=10
        )
        redirect = Redirect(
            redirect_url="/bandwidth/webhooks/voice/redirect"
        )
        response = BxmlResponse([speak_sentence, ring, redirect])
        return Response(status_code=200, content=response.to_bxml(), media_type="application/xml")


@app.post("/bandwidth/webhooks/voice/redirect")
def handle_inbound_call(callback: RedirectCallback):
    logger.info(f"Received redirected call from {callback.var_from}")
    logger.debug(callback)
    ring = Ring(
        duration=10
    )
    redirect = Redirect(
        redirect_url="/bandwidth/webhooks/voice/redirect"
    )
    response = BxmlResponse([ring, redirect])
    return Response(status_code=200, content=response.to_bxml(), media_type="application/xml")


def start_server(port: int):
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        log_level="debug",
        reload=True,
    )


if __name__ == "__main__":
    start_redis_listener()
    start_server(8080)
