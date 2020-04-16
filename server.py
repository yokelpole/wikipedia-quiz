from quiz import get_question_and_answers
from bottle import Bottle, response, request, route, run, static_file

import time, threading
import json

HOSTNAME = "localhost"
PORT = 8080

active_users = []
active_question = None

app = Bottle()

def update_question_timer():
  global active_question
  active_question = get_question_and_answers()
  threading.Timer(10, update_question_timer).start()

update_question_timer()

@app.route("/")
def base():
  return static_file("page.html", "./")

@app.route("/get_current_question")
def get_current_question():
  global active_question
  response.content_type = "text/json; charset=UTF-8"
  return active_question

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
