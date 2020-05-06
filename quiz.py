from bs4 import BeautifulSoup
from shared import get_html_facts
import asyncio
import random
import json
import os
import sys

CONFIDENCE_LEVEL = 0.4
NUMBER_OF_ANSWERS = 4
INVALID_CATEGORIES = ["date"]

def data_files_exist_and_have_data(topic, section):
  if (os.path.exists(file_prefix(topic, section) + "_fact_links.json") == False or
      os.path.exists(file_prefix(topic, section) + "_fulltext_metadata.json") == False):
        return False
  if (os.stat(file_prefix(topic, section) + "_fact_links.json").st_size == 0 and
      os.stat(file_prefix(topic, section) + "_fulltext_metadata.json").st_size == 0):
        return False

  return True

def file_prefix(topic, section):
  return "quiz_content/" + topic + "_" + section

def get_valid_categories(facts, facts_metadata):
  category_count = {}

  for answer_list in facts_metadata:
    for answer in answer_list:
      if answer == False:
        continue      
      if answer["confidence"] < CONFIDENCE_LEVEL:
        continue

      if not answer["category"] in category_count:
        category_count[answer["category"]] = 1
      else:
        category_count[answer["category"]] += 1 

  valid_categories = []
  for category, count in category_count.items():
    if category in INVALID_CATEGORIES:
      continue

    if count >= NUMBER_OF_ANSWERS:
      valid_categories.append(category)

  return valid_categories

def get_question_and_answers(topic = None, section = None):
  if topic == None and section == None:
    # Cycle through the available quiz data and ask a question
    metadata_files = list(filter(lambda x: x.find("fulltext_metadata.json") != -1, os.listdir("quiz_content")))
    metadata_filename = random.choice(metadata_files)
    fulltext_metadata = json.loads(open("quiz_content/" + metadata_filename, "r").read())
    topic = fulltext_metadata["topic"]
    section = fulltext_metadata["section"]
  else:
    if not os.path.exists("quiz_content/" + topic + "_page.html") and os.stat("quiz_content/" + topic + "_page.html"):
      print ("### Quiz data not found - use crawler.py to generate data")    
      return
    if not data_files_exist_and_have_data(topic, section):
      print("### Quiz data not found - use crawler.py to generate data")
      return
    fulltext_metadata = json.loads(open(file_prefix(topic, section) + "_fulltext_metadata.json", "r").read())
 
  html = BeautifulSoup(open("quiz_content/" + topic + "_page.html", "r").read(), "html.parser")
  html_facts = get_html_facts(html, section)
  fact_links = json.loads(open(file_prefix(topic,section) + "_fact_links.json", "r").read())
  facts_metadata = fulltext_metadata["facts"]
  valid_categories = get_valid_categories(html_facts, facts_metadata)
    
  if len(valid_categories) == 0:
    print("### Not enough valid categories for this topic/section: " + topic + " " + section)
    return

  # Ensure that the answer exists in the questions - when the lookup fails
  # there's the possibility of a link not containing a fact
  is_valid_fact = False
  while not is_valid_fact:
    question_number = random.randint(0, len(html_facts)-1)
    question = html_facts[question_number]
    if len(question.select("a[title]")) == 0:
      continue

    answer_fact_number = random.randint(0, len(question.select("a[title]"))-1)
    # This is a hack to get around when certain answers have been dropped.
    if answer_fact_number >= len(facts_metadata[question_number]):
      answer_fact_number = len(facts_metadata[question_number]) - 1 

    fact_metadata = facts_metadata[question_number][answer_fact_number]

    if int(answer_fact_number) >= len(facts_metadata[question_number]):
      continue

    if fact_metadata == False:
      continue

    if fact_metadata["category"] in INVALID_CATEGORIES or fact_metadata["category"] not in valid_categories:
      continue

    is_valid_fact = True
  
  answer_fact_category = fact_metadata["category"]
  answer_dictionary = facts_metadata[question_number][answer_fact_number]
  answers = [answer_dictionary["fact"]]

  while len(answers) < NUMBER_OF_ANSWERS or len(answers) == len(fact_links[answer_fact_category]) - 1:
    location = random.choice(fact_links[answer_fact_category])
    fact_metadata = facts_metadata[location[0]][int(location[1])]
    possible_answer = fact_metadata["fact"]

    if fact_metadata["confidence"] < CONFIDENCE_LEVEL:
      continue

    if not possible_answer in answers:
      answers.append(possible_answer)

  question.select("a")[int(answer_fact_number)].replace_with("_________________")

  random.shuffle(answers)

  return {
    "answers": answers,
    "correct_answer": answer_dictionary["fact"],
    "topic": topic,
    "section": section,
    "question": question.text
  }

def ask_question(topic = None, section = None):
  question_and_answers_dict = get_question_and_answers(topic, section)
  question = question_and_answers_dict["question"]
  answers = question_and_answers_dict["answers"]
  correct_answer = question_and_answers_dict["correct_answer"]
  topic = question_and_answers_dict["topic"]
  section = question_and_answers_dict["section"]

  print("TOPIC: " + topic.replace("_", " "))
  print("CATEGORY: " + section.replace("_", " "))
  print(question)
  user_answer = ""

  for i, value in enumerate(answers):
    print(i + 1, ": " + value)

  # FIXME: Make this work with NUMBER_OF_ANSWERS
  while user_answer != "1" and user_answer != "2" and user_answer != "3" and user_answer != "4":
    user_answer = input("[1,2,3, or 4]: ").lower()
  
  if answers[int(user_answer)-1] == correct_answer:
    print("Correct! 🙋\n\n")
    return True
  else:
    print("Wrong. 😓")
    print("The correct answer is: " + correct_answer + "\n\n")
    return False

if __name__ == "__main__":        
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
