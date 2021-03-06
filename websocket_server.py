from quiz import get_question_and_answers

import time
import datetime
import threading
import uuid
import json
import websockets
import asyncio
import ssl
import os

HOSTNAME = "127.0.0.1" if "LOCAL" in os.environ else "kylepoole.me"
PORT = 8080
QUESTION_TIME = 20
WAIT_TIME = 10

active_users = {}
connected = set()
active_question = None
active_question_finish_time = None

def get_new_active_question_finish_time():
  return datetime.datetime.utcnow() + datetime.timedelta(0, QUESTION_TIME)


def get_active_question_message():
  global active_question
  return json.dumps({
    "type": "question_changed",
    "value": {
      "question": dict(
        filter(
          lambda item: item[0] != "correct_answer",
          active_question.items()
        )
      ),
      "finish_time": active_question_finish_time.isoformat(),
    },
  })

async def send_to_clients(message):
  return await asyncio.wait(
    [connection.send(message) for connection in connected]
  )


async def update_question(websocket, path):
  global active_question, active_question_finish_time, active_users
  if datetime.datetime.utcnow() > active_question_finish_time and active_question:
    await send_to_clients(json.dumps({
      "type": "correct_answer",
      "value": active_question["correct_answer"]
    }))
    await asyncio.sleep(WAIT_TIME)
    active_question = None
    while not active_question:
      active_question = get_question_and_answers()
    active_question_finish_time = get_new_active_question_finish_time()
    for _, value in active_users.items():
      value["answered_correctly"] = None
    await send_to_clients(get_active_question_message())
    await update_leaderboard()
  else:
    await asyncio.sleep(0.1)


async def update_leaderboard():
  global active_users
  if len(active_users) == 0:
    return

  return await send_to_clients(json.dumps({
    "type": "leaderboard_updated",
    "value": active_users,
  }))

async def consumer_handler(websocket, path):
  global active_users

  recv_socket = await websocket.recv()
  recv_data = json.loads(recv_socket)
  # TODO: Handle when player answers a question
  if recv_data["type"] == "register_player":
    player_id = str(uuid.uuid4())
    websocket.player_id = player_id
    active_users[player_id] = {
      "name": recv_data["value"]["name"],
      "score": 0,
      "answered_correctly": None,
    }

    await send_to_clients(json.dumps({
      "type": "player_registered",
      "value": {
        "player_id": player_id,
        # This is probably insecure if somebody registers with the same name
        # at the same time - but edge case for sure
        "name": recv_data["value"]["name"]
      },
    }))
    await update_leaderboard()
  if recv_data["type"] == "player_answer":
    # only send correct answer to player
    await websocket.send(json.dumps({
      "type": "correct_answer",
      "value": active_question["correct_answer"]
    }))

    targeted_user = active_users[recv_data["value"]["player_id"]]

    if active_question["correct_answer"] == recv_data["value"]["answer"]:
      targeted_user["score"] = targeted_user["score"] + 1
      targeted_user["answered_correctly"] = True
    else:
      targeted_user["answered_correctly"] = False

    await update_leaderboard()

async def connection_loop(websocket, path):
  connected.add(websocket)

  try:
    await websocket.send(json.dumps({
      "type": "server_time",
      "value": datetime.datetime.utcnow().isoformat(),
    }))
    await websocket.send(get_active_question_message())
    while True and websocket.open:
      question_update_task = asyncio.ensure_future(update_question(websocket, path))
      consumer_task = asyncio.ensure_future(consumer_handler(websocket, path))
      _, pending = await asyncio.wait(
        [
          question_update_task,
          consumer_task,
        ],
        return_when=asyncio.FIRST_COMPLETED,
      )
      for task in pending:
        task.cancel()
  finally:
    connected.remove(websocket)
    if hasattr(websocket, 'player_id'):
      active_users.pop(websocket.player_id, None)
    await update_leaderboard()

active_question = get_question_and_answers()
active_question_finish_time = get_new_active_question_finish_time()
if "LOCAL" not in os.environ:
  ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
  ssl_context.load_cert_chain('cert_location', 'private_key_location')
  start_server = websockets.serve(connection_loop, HOSTNAME, PORT, ssl=ssl_context)
else:
  start_server = websockets.serve(connection_loop, HOSTNAME, PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()