from quiz import get_question_and_answers
from bottle import Bottle, response, request, route, run, static_file

import time, datetime, threading
import uuid
import json

HOSTNAME = "localhost"
PORT = 8090
QUESTION_TIME = 10

active_users = []
active_question = None
active_question_start_time = None

app = Bottle()

class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors

app.install(EnableCors())


def update_question_timer():
  print("### UPDATING QUESTION")
  global active_question, active_question_start_time
  # Activate timer before fetching question in case get_questions_and_answers fails
  # FIXME: Make it so get_questions_and_answers fails more gracefully
  threading.Timer(QUESTION_TIME, update_question_timer).start()

  active_question = get_question_and_answers()
  active_question_start_time = datetime.datetime.utcnow()

update_question_timer()

@app.route("/get_current_question")
def get_current_question():
  global active_question, active_question_start_time
  response.content_type = "text/json; charset=UTF-8"
  return {
    **active_question,
    "active_question_start_time": active_question_start_time.isoformat(),
    "question_time": QUESTION_TIME,
    "players": active_users,
  }



@app.route("/answer_question", method=["OPTIONS", "POST"])
def answer_question():
  try:
    json = request.json
  except:
    raise ValueError 

  for user in active_users:
    if user["name"] == json["name"] and json["correct"] == True:
      user["score"] += 1
  return active_question

@app.route("/get_players")
def get_players():
  response.content_type = "text/json; charset=UTF-8"
  return {
    "players": active_users
  }

@app.route("/join_game", method=["OPTIONS", "POST"])
def join_game():
  try:
    json = request.json
  except:
    raise ValueError

  user_id = str(uuid.uuid4())
  active_users.append({
    "name": json["name"],
    "id": user_id,
    "score": 0,
  })
  return { "ID": user_id }

@app.route("/leave_game", method="POST")
def leave_game():
  # let a player leave the game
  request.forms.get('id')
  return

run(app, host=HOSTNAME, port=PORT)
