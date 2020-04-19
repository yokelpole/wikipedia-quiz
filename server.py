from quiz import get_question_and_answers
from bottle import Bottle, response, request, route, run, static_file

import time, datetime, threading
import json

HOSTNAME = "localhost"
PORT = 8080
QUESTION_TIME = 10

active_users = []
active_question = None
active_question_start_time = None

app = Bottle()

def update_question_timer():
  print("### UPDATING QUESTION")
  global active_question, active_question_start_time
  # Activate timer before fetching question in case get_questions_and_answers fails
  # FIXME: Make it so get_questions_and_answers fails more gracefully
  threading.Timer(QUESTION_TIME, update_question_timer).start()

  active_question = get_question_and_answers()
  active_question_start_time = datetime.datetime.utcnow()

update_question_timer()

@app.route("/")
def base():
  return static_file("page.html", "./")

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

@app.route("/answer_question", method="POST")
def answer_question():
  try:
    json = request.json
  except:
    raise ValueError 

  for user in active_users:
    print(json)
    print(user)
    if user["name"] == json["name"] and json["correct"] == True:
      user["score"] += 1
  return active_question

@app.route("/get_players")
def get_players():
  response.content_type = "text/json; charset=UTF-8"
  print(active_users)
  return {
    "players": active_users
  }

@app.route("/join_game", method="POST")
def join_game():
  try:
    json = request.json
  except:
    raise ValueError

  user_id = 123
  active_users.append({
    "name": json["name"],
    "ID": user_id,
    "score": 0,
  })
  return { "ID": user_id }

@app.route("/leave_game", method="POST")
def leave_game():
  # let a player leave the game
  request.forms.get('id')
  return

run(app, host=HOSTNAME, port=PORT)
