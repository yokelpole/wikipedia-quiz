from http.server import BaseHTTPRequestHandler, HTTPServer
from quiz import get_question_and_answers

import json

HOSTNAME = "localhost"
PORT = 8080

class Server(BaseHTTPRequestHandler):
  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/json")
    self.end_headers()
    self.wfile.write(bytearray(json.dumps(get_question_and_answers()), 'utf-8'))

  def do_POST(self):
    print("### COMING")
    self.send_response(200)
    self.send_header("Content-type", "text/json")
    self.end_headers()

active_server = HTTPServer((HOSTNAME, PORT), Server)
print("Up and running at http://%s:%s" % (HOSTNAME, PORT))

try:
  active_server.serve_forever()
except KeyboardInterrupt:
  pass

active_server.server_close()
print("Finito")