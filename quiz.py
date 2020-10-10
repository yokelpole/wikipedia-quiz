from bs4 import BeautifulSoup
from shared import get_html_questions
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

def get_answer_category(answer, facts_metadata):
  for category in facts_metadata:
    if answer.lower() in facts_metadata[category]:
      return category

def get_valid_categories(facts_metadata):
  category_count = {}

  for category in facts_metadata:
    for fact in facts_metadata[category]:
      value = facts_metadata[category][fact]
      if value["confidence"] < CONFIDENCE_LEVEL:
        continue

      if not category in category_count:
        category_count[category] = 1
      else:
        category_count[category] += 1

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
  html_questions = get_html_questions(html, section)
  facts_metadata = fulltext_metadata["facts"]
  valid_categories = get_valid_categories(facts_metadata)

  if len(valid_categories) == 0:
    print("### Not enough valid categories for this topic/section: " + topic + " " + section)
    return

  is_valid_fact = False
  while not is_valid_fact:
    question_number = random.randint(0, len(html_questions)-1)
    question = html_questions[question_number]

    if question.select("a[title]") == []:
      continue

    answer_fact_number = random.randint(0, len(question.select("a[title]"))-1)
    answer = question.select("a[title]")[answer_fact_number]["title"]
    category = get_answer_category(answer, facts_metadata)

    if category in INVALID_CATEGORIES or category not in valid_categories:
      continue

    is_valid_fact = True

  answers = [answer]

  while len(answers) < NUMBER_OF_ANSWERS:
    possible_answer_data = facts_metadata[category][random.choice(list(facts_metadata[category]))]
    if possible_answer_data["confidence"] < CONFIDENCE_LEVEL:
      continue

    if not possible_answer_data["fact"] in answers:
      answers.append(possible_answer_data["fact"])

  question.select("a")[int(answer_fact_number)].replace_with("_________________")

  random.shuffle(answers)

  return {
    "answers": answers,
    "correct_answer": answer,
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