from bs4 import BeautifulSoup
from shared import get_html_facts
import asyncio
import random
import json
import os
import sys

def data_files_exist_and_have_data(topic, start_header_text):
  file_prefix = "quiz_content/" + topic + "_" + start_header_text

  if (os.path.exists(file_prefix + "_fact_links.json") == False or
      os.path.exists(file_prefix + "_fulltext_metadata.json") == False):
        return False
  if (os.stat(file_prefix + "_fact_links.json").st_size == 0 and
      os.stat(file_prefix + "_fulltext_metadata.json").st_size == 0):
        return False

  return True

def main(topic, start_header_text = "Events"):
  # Grab the links from the facts and attempt to categorize them.
  # Need a data shape that will let us know where in the fact list the link belongs to.
  if not os.path.exists("quiz_content/" + topic + "_page.html") and os.stat("quiz_content/" + topic + "_page.html"):
    print ("### Quiz data not found - use crawler.py to generate data")    
  # TODO: Break the gathering data out into its own file
  if not data_files_exist_and_have_data(topic, start_header_text):
    print("### Quiz data not found - use crawler.py to generate data")
    return

  html = BeautifulSoup(open("quiz_content/" + topic + "_page.html", "r").read(), "html.parser")
  html_facts = get_html_facts(html, start_header_text)
  file_prefix = "quiz_content/" + topic + "_" + start_header_text
  fact_links = json.loads(open(file_prefix + "_fact_links.json", "r").read())
  fulltext_metadata = json.loads(open(file_prefix + "_fulltext_metadata.json", "r").read())
    
  # Ensure that the answer exists in the questions - when the lookup fails
  # there's the possibility of a link not containing a fact
  is_valid_fact = False
  while not is_valid_fact:  
    question_number = random.randint(0, len(html_facts)-1)
    question = html_facts[question_number]
    answer_fact_number = random.randint(0, len(question.select("a"))-1)

    if int(answer_fact_number) > len(fulltext_metadata[question_number]):
      continue

    if fulltext_metadata[question_number][answer_fact_number] == False:
      continue

    # Do not let the blank be a date as it does not work well.
    answer_fact_category = fulltext_metadata[question_number][answer_fact_number]["category"]
    if answer_fact_category == "DATE" and answer_fact_number == 0:
      continue

    # TODO: Make the # of questions for a topic customizable
    if len(fact_links[answer_fact_category]) <= 4:
      continue

    is_valid_fact = True
  
  answer_dictionary = fulltext_metadata[question_number][answer_fact_number]
  possible_answers = [answer_dictionary["fact"]]

  # FIXME: This is the cause of the freezes that happen sometimes.
  # Might need a qualifier for the initial question to ensure there are enough answers.
  while len(possible_answers) < 4 or len(possible_answers) == len(fact_links[answer_fact_category]) - 1:
    location = random.choice(fact_links[answer_fact_category])
    possible_answer = fulltext_metadata[location[0]][int(location[1])]["fact"]

    if not possible_answer in possible_answers:
      possible_answers.append(possible_answer)

  question.select("a")[int(answer_fact_number)].replace_with("_________________")

  random.shuffle(possible_answers)

  print(question.text)
  # print("ANSWER IS " + str(answer_dictionary["fact"]))
  print(str(possible_answers))

if len(sys.argv) < 3:
  print("Not enough parameters specified.\n Intended use: 'parser.py [topic] [header_text]'")
else:
  main(sys.argv[1].replace(" ", "_"), sys.argv[2])
