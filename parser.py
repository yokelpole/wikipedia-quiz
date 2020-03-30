from bs4 import BeautifulSoup
import urllib.request
import wikipedia
import asyncio
import random
import re
import json
import os
import sys

def get_html_facts(html):
  # On the music summary pages this will grab the "events"
  # that happened for a given year.
  elements = []
  element = html.select("h2>span[id='Events']")[0].parent
  
  # Only rip data between the two <h2>s
  cut_off_element = element.find_next("h2")

  while element != cut_off_element:
    if hasattr(element, "select") == False:
      element = element.next_element
      continue
    if element.select("ul li") and not element.select("ul li ul"):
      elements.extend(element.select("ul li"))
    element = element.next_element

  # Ensure that we have more than one anchor element - anything with less is
  # unlikely to be a quizzable fact.
  return list(filter(lambda x: len(x.select("a")), elements))

def fetch_and_parse_html(topic):
  # TODO: We should save the output of the HTML as well to ensure it syncs up
  # with fact_links and fulltext_metadata.
  print("### " + topic + " does not exist - fetching data")
  html = urllib.request.urlopen(wikipedia.page(topic).url).read().decode("utf-8")
  parsed_html = BeautifulSoup(html, "html.parser")
  
  html_file = open(topic + "_page.html", "w")
  html_file.truncate(0)
  html_file.write(html)
  html_file.close()

  html_facts = get_html_facts(parsed_html)

  # TODO: Does this need to go?
  fact_links = {
    "location": [],
    "person": [],
    "band": [],
    "song": [],
    "album": [],
    "genre": [],
    "event": [],
    "date": [],
    "award": [],
    "uncategorized": []
  }
  fulltext_metadata = []

  for base_index, facts in enumerate(html_facts):
    current_set = {}
    for question_index, current_fact in enumerate(facts):
      # FIXME: Is there a better way to duck type this?
      if not hasattr(current_fact, "select"):
        continue
      
      try:
        if not current_fact["title"]:
          continue

        title = current_fact["title"].casefold()
        summary = wikipedia.summary(title, sentences = 2)
        category = categorize(summary)
        current_set[question_index] = {
          "fact": current_fact.text,
          "summary": summary,
          "category": category 
        }
        fact_links[category].append((base_index, question_index))
      except Exception as e:
        print("There was an error with retrieving from wikipedia for " + current_fact.text, " aka " + title)
        print(e)

    fulltext_metadata.append(current_set)

  fact_links_file = open(topic + "_fact_links.json", "w")
  fact_links_file.truncate(0)
  fact_links_file.write(json.dumps(fact_links))
  fact_links_file.close()

  fulltext_metadata_file = open(topic + "_fulltext_metadata.json", "w")
  fulltext_metadata_file.truncate(0)
  fulltext_metadata_file.write(json.dumps(fulltext_metadata))
  fulltext_metadata_file.close()

  return {
    "html_facts": html_facts,
    "fact_links": fact_links,
    "fulltext_metadata": fulltext_metadata,
  }

def categorize(summary):
  categories = {
    "song": [
      " song ",
      " composition ",
    ],
    "location": [
      " located in ",
      " city ",
      " university ",
      " county ",
      " town "
    ],
    "band": [
      " band",
      " artist",
      " group",
      " duo "
    ],
    "album": [
      " album",
      " compilation"
    ],
    "event": [
      " event",
      " festival",
      " tour",
      " protest",
      " occurred"
    ],
    "genre": [
      "genre"
    ],
    "person": [
      " woman ",
      " man ",
      " he ",
      " her ",
      " his ",
      " she ",
      " they ",
      " singer",
      " actress",
      " songwriter",
      " activist",
      " bassist",
      " guitarist",
      " musician",
      " director",
      " writer",
      " composer",
      " dancer",
      "husband ",
      "wife ",
    ],
    "date": [
      "january ",
      "february ",
      "march ",
      "april ",
      "may ",
      "june ",
      "july ",
      "august ",
      "september ",
      "october ",
      "november ",
      "december ",
      "monday ",
      "tuesday ",
      "wednesday ",
      "thursday ",
      "friday ",
      "saturday ",
      "sunday "
    ]
  }

  scores = {}
  for category in categories:
    scores[category] = 0

  for sentence in summary.split("."):
    for category in categories:
      for value in categories[category]:
        if sentence.casefold().find(value) > -1:
          scores[category] += 1

  highestScore = { "category": "uncategorized", "score": 0 }
  for category in scores:
    if highestScore["score"] < scores[category]:
      highestScore = { "category": category, "score": scores[category] }

  return highestScore["category"]

def files_exist_and_have_data(topic):
  if (os.path.exists(topic + "_page.html") == False or 
      os.path.exists(topic + "_fact_links.json") == False or
      os.path.exists(topic + "_fulltext_metadata.json") == False):
        return False
  if (os.stat(topic + "_page.html").st_size == 0 and
      os.stat(topic + "_fact_links.json").st_size == 0 and
      os.stat(topic + "_fulltext_metadata.json").st_size == 0):
        return False

  return True

def main(topic):
  # Grab the links from the facts and attempt to categorize them.
  # Need a data shape that will let us know where in the fact list the link belongs to.
  if files_exist_and_have_data(topic):
    html = BeautifulSoup(open(topic + "_page.html", "r").read(), "html.parser")
    html_facts = get_html_facts(html)
    fact_links = json.loads(open(topic + "_fact_links.json", "r").read())
    fulltext_metadata = json.loads(open(topic + "_fulltext_metadata.json", "r").read())
  else:
    new_data = fetch_and_parse_html(topic)
    html_facts = get_html_facts(new_data["html_facts"]) 
    fact_links = new_data["fact_links"]
    fulltext_metadata = new_data["fulltext_metadata"]

  # Ensure that the answer exists in the questions - when the lookup fails
  # there's the possibility of a link not containing a fact
  is_valid_fact = False
  while not is_valid_fact:
    question_number = random.randint(0, len(html_facts)-1)
    question = html_facts[question_number]
    answer_fact_number = random.randint(0, len(question.select("a"))-1)
    
    if not str(answer_fact_number*2) in fulltext_metadata[question_number]:
      continue

    # Do not let the blank be a date as it does not work well.
    answer_fact_category = fulltext_metadata[question_number][str(answer_fact_number*2)]["category"]
    if answer_fact_category == "date" and answer_fact_number == 0:
      continue

    is_valid_fact = True
  
  answer_dictionary = fulltext_metadata[question_number][str(answer_fact_number*2)]
  possible_answers = [answer_dictionary["fact"]]

  while len(possible_answers) < 4 or len(possible_answers) == len(fact_links[answer_fact_category]) - 1:
    location = random.choice(fact_links[answer_fact_category])
    possible_answer = fulltext_metadata[location[0]][str(location[1])]["fact"]

    if not possible_answer in possible_answers:
      possible_answers.append(possible_answer)

  question.select("a")[answer_fact_number].replace_with("_________________")

  random.shuffle(possible_answers)

  print(question.text)
  # print("ANSWER IS " + str(answer_dictionary["fact"]))
  print(str(possible_answers))

main(sys.argv[1].replace(" ", "_"))