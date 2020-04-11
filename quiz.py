from bs4 import BeautifulSoup
from shared import get_html_facts
import asyncio
import random
import json
import os
import sys

def data_files_exist_and_have_data(topic, section):
  file_prefix = "quiz_content/" + topic + "_" + section

  if (os.path.exists(file_prefix + "_fact_links.json") == False or
      os.path.exists(file_prefix + "_fulltext_metadata.json") == False):
        return False
  if (os.stat(file_prefix + "_fact_links.json").st_size == 0 and
      os.stat(file_prefix + "_fulltext_metadata.json").st_size == 0):
        return False

  return True
  

def ask_question(topic = None, section = None):
  if topic == None and section == None:
    html_facts = [] 
    while len(html_facts) <= 1:
      current_metadata_file_name = random.choice(metadata_files)
      current_metadata_file = json.loads(open("quiz_content/" + current_metadata_file_name, "r").read())
      topic = current_metadata_file["topic"]
      section = current_metadata_file["section"]

      # TODO: Add a check ensuring at least one category has enough questions to ask.
      # 1986 in music "Events" currently freezes because of this.
      # Or at least do an early escape.
      html = BeautifulSoup(open("quiz_content/" + topic + "_page.html", "r").read(), "html.parser")
      html_facts = get_html_facts(html, section)
  else:
    # Grab the links from the facts and attempt to categorize them.
    # Need a data shape that will let us know where in the fact list the link belongs to.
    if not os.path.exists("quiz_content/" + topic + "_page.html") and os.stat("quiz_content/" + topic + "_page.html"):
      print ("### Quiz data not found - use crawler.py to generate data")    
    if not data_files_exist_and_have_data(topic, section):
      print("### Quiz data not found - use crawler.py to generate data")
      return
    html = BeautifulSoup(open("quiz_content/" + topic + "_page.html", "r").read(), "html.parser")
    html_facts = get_html_facts(html, section)
 
  file_prefix = "quiz_content/" + topic + "_" + section
  fact_links = json.loads(open(file_prefix + "_fact_links.json", "r").read())
  fulltext_metadata = json.loads(open(file_prefix + "_fulltext_metadata.json", "r").read())
  facts_metadata = fulltext_metadata["facts"]
    
  # Ensure that the answer exists in the questions - when the lookup fails
  # there's the possibility of a link not containing a fact
  is_valid_fact = False
  while not is_valid_fact:
    print(html_facts)
    question_number = random.randint(0, len(html_facts)-1)
    question = html_facts[question_number]
    answer_fact_number = random.randint(0, len(question.select("a"))-1)

    if int(answer_fact_number) >= len(facts_metadata[question_number]):
      continue

    if facts_metadata[question_number][answer_fact_number] == False:
      continue

    # Do not let the blank be a date as it does not work well.
    answer_fact_category = facts_metadata[question_number][answer_fact_number]["category"]
    if answer_fact_category == "date" and answer_fact_number == 0:
      continue

    # TODO: Make the # of questions for a topic customizable
    if len(fact_links[answer_fact_category]) <= 4:
      continue

    # valid_facts = 0
    # for location in fact_links[answer_fact_category]:
    #   confidence = facts_metadata[location[0]][int(location[1])]["confidence"]
    #   if confidence > 0.5:
    #     valid_facts += 1

    # if valid_facts <= 4:
    #   continue

    is_valid_fact = True
  
  answer_dictionary = facts_metadata[question_number][answer_fact_number]
  possible_answers = [answer_dictionary["fact"]]

  # FIXME: This is the cause of the freezes that happen sometimes.
  # Might need a qualifier for the initial question to ensure there are enough answers.
  while len(possible_answers) < 4 or len(possible_answers) == len(fact_links[answer_fact_category]) - 1:
    location = random.choice(fact_links[answer_fact_category])
    fact_metadata = facts_metadata[location[0]][int(location[1])]
    confidence = fact_metadata["confidence"]
    possible_answer = fact_metadata["fact"]

    # TODO: Make the confidence amount a variable
    if fact_metadata["confidence"] < 0.5:
      continue

    if not possible_answer in possible_answers:
      possible_answers.append(possible_answer)

  question.select("a")[int(answer_fact_number)].replace_with("_________________")

  random.shuffle(possible_answers)

  print("TOPIC: " + topic.replace("_", " "))
  print("CATEGORY: " + section.replace("_", " "))
  print(question.text)
  # print("ANSWER IS " + str(answer_dictionary["fact"]))
  user_answer = ""

  for i, value in enumerate(possible_answers):
    print(i + 1, ": " + value)

  while user_answer != "1" and user_answer != "2" and user_answer != "3" and user_answer != "4":
    user_answer = input("[1,2,3, or 4]: ").lower()
  
  if possible_answers[int(user_answer)-1] == answer_dictionary["fact"]:
    print("Correct! 🙋\n\n")
    return True
  else:
    print("Wrong. 😓")
    print("The correct answer is: " + answer_dictionary["fact"] + "\n\n")
    return False

# Cycle through the available quiz data and ask a question
metadata_files = list(filter(lambda x: x.find("fulltext_metadata.json") != -1, os.listdir("quiz_content")))
asked = 0
correct = 0

if len(sys.argv) >= 3:
  ask_question(sys.argv[1].replace(" ", "_"), sys.argv[2])
else:
  while asked < 5:
    if ask_question():
      correct += 1
    asked += 1 
  print("You got " + str(correct) + " questions right.")

print("### GAME OVER")
