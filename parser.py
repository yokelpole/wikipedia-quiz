from bs4 import BeautifulSoup
import urllib.request
import wikipedia
import asyncio
import random
import re
import json
import os
import sys
import spacy

def get_html_facts(html, start_header_text):
  # On the music summary pages this will grab the "events"
  # that happened for a given year.
  elements = []
  element = html.select("h2>span[id='" + start_header_text + "']")[0].parent
  
  # Only rip data between the two <h2>s
  cut_off_element = element.find_next("h2")

  while element != cut_off_element:
    if hasattr(element, "select") == False:
      element = element.next_element
      continue
    if element.select("li") and not element.select("li ul"):
      elements.extend(element.select("li"))
    element = element.next_element

  # Ensure that we have more than one anchor element - anything with less is
  # unlikely to be a quizzable fact.
  return list(filter(lambda x: len(x.select("a")), elements))

def get_and_save_html(topic):
  # TODO: We should save the output of the HTML as well to ensure it syncs up
  # with fact_links and fulltext_metadata.
  print("### " + topic + " does not exist - fetching data")
  html = urllib.request.urlopen(wikipedia.page(topic).url).read().decode("utf-8")
  parsed_html = BeautifulSoup(html, "html.parser")
  
  html_file = open(topic + "_page.html", "w")
  html_file.truncate(0)
  html_file.write(html)
  html_file.close()

  return parsed_html

def get_facts_and_metadata_from_html(html, topic, start_header_text):
  nlp = spacy.load("en_core_web_md")

  html_facts = get_html_facts(html, start_header_text)

  # TODO: Does this need to go?
  fact_links = {}
  fulltext_metadata = []

  for base_index, facts in enumerate(html_facts):
    current_set = []
    for question_index, current_fact in enumerate(facts):
      # FIXME: Is there a better way to duck type this?
      if not hasattr(current_fact, "select"):
        continue
      
      try:
        if not current_fact["title"]:
          continue

        title = current_fact["title"].casefold()
        summary = wikipedia.summary(title, sentences = 3)
        nlp_summary = nlp(summary)
        category = nlp_summary.ents[0].label_
        # category = categorize(summary)
        current_set.append({
          "fact": current_fact.text,
          "summary": summary,
          "category": category
        })
        print(current_set[len(current_set)-1])
        # fact_data_file = open("./data/" + category + "/" + title + "_fact_data.txt", "w")
        # fact_data_file.truncate(0)
        # fact_data_file.write(summary)
        if category not in fact_links:
          fact_links[category] = []
        fact_links[category].append((base_index, len(current_set)-1))
      except Exception as e:
        current_set.append(False)
        print("There was an error with retrieving from wikipedia for " + current_fact.text, " aka " + title)
        print(e)

    fulltext_metadata.append(current_set)

  fact_links_file = open(topic + "_" + start_header_text + "_fact_links.json", "w")
  fact_links_file.truncate(0)
  fact_links_file.write(json.dumps(fact_links))
  fact_links_file.close()

  fulltext_metadata_file = open(topic + "_" + start_header_text + "_fulltext_metadata.json", "w")
  fulltext_metadata_file.truncate(0)
  fulltext_metadata_file.write(json.dumps(fulltext_metadata))
  fulltext_metadata_file.close()

  return {
    "html_facts": html_facts,
    "fact_links": fact_links,
    "fulltext_metadata": fulltext_metadata,
  }

def data_files_exist_and_have_data(topic, start_header_text):
  file_prefix = topic + "_" + start_header_text

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
  if os.path.exists(topic + "_page.html") and os.stat(topic + "_page.html"):
    html = BeautifulSoup(open(topic + "_page.html", "r").read(), "html.parser")
  else:
    html = get_and_save_html(topic)
 
  if data_files_exist_and_have_data(topic, start_header_text):
    html_facts = get_html_facts(html, start_header_text)
    file_prefix = topic + "_" + start_header_text
    fact_links = json.loads(open(file_prefix + "_fact_links.json", "r").read())
    fulltext_metadata = json.loads(open(file_prefix + "_fulltext_metadata.json", "r").read())
  else:
    new_data = get_facts_and_metadata_from_html(html, topic, start_header_text)
    html_facts = get_html_facts(new_data["html_facts"], start_header_text) 
    fact_links = new_data["fact_links"]
    fulltext_metadata = new_data["fulltext_metadata"]

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

    is_valid_fact = True
  
  answer_dictionary = fulltext_metadata[question_number][answer_fact_number]
  possible_answers = [answer_dictionary["fact"]]

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
