from bs4 import BeautifulSoup
import urllib.request
import wikipedia
import asyncio
import random
import re
import json
import os

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
      " band ",
      " artist ",
      " group ",
      " duo "
    ],
    "album": [
      " album ",
      " compilation "
    ],
    "event": [
      " event ",
      " festival ",
      " tour ",
    ],
    "genre": [
      " genre "
    ],
    "person": [
      " woman ",
      " man ",
      " he ",
      " her ",
      " his ",
      " she ",
      " they ",
      " singer ",
      " actress ",
      " singer-songwriter ",
      " activist ",
      " bassist ",
      " guitarist ",
      " musician ",
      " director ",
      " writer ",
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
  for category in categories:
    for value in categories[category]:
      # TODO: Some kind of weighting?
      if summary.casefold().find(value) > -1:
        return category
  return "uncategorized"

def main():
  # TODO: We should save the output of the HTML as well to ensure it syncs up
  # with fact_links and fulltext_metadata.
  html = urllib.request.urlopen(wikipedia.page("2000 in music").url).read()
  parsed_html = BeautifulSoup(html, "html.parser")
  
  # On the music summary pages this will grab the "events"
  # that happened for a given year.
  elements = []
  element = parsed_html.select("h2>span[id='Events']")[0].parent
  
  # Only rip data between the two <h2>s
  cut_off_element = element.find_next("h2")

  # FIXME: This might be able to be done with a map
  while element != cut_off_element:
    if hasattr(element, "select") == False:
      element = element.next_element
      continue
    if element.select("ul li") and not element.select("ul li ul"):
      elements.extend(element.select("ul li"))
    element = element.next_element

  # Ensure that we have more than one anchor element - anything with less is
  # unlikely to be a quizzable fact.
  music_facts = list(filter(lambda x: len(x.select("a")), elements))

  # Grab the links from the facts and attempt to categorize them.
  # Need a data shape that will let us know where in the fact list the link belongs to.
  if os.stat("fact_links.json").st_size != 0 and os.stat("fulltext_metadata.json").st_size != 0:
    fact_links = json.loads(open("fact_links.json", "r").read())
    fulltext_metadata = json.loads(open("fulltext_metadata.json", "r").read())
  else:
    fact_links = {
      "location": [],
      "person": [],
      "band": [],
      "song": [],
      "album": [],
      "genre": [],
      "event": [],
      "date": [],
      "award": []
    }
    fulltext_metadata = []

    for base_index, facts in enumerate(music_facts):
      print(str(base_index) + " " + str(facts))
      current_set = {}
      for question_index, current_fact in enumerate(facts):
        # FIXME: Is there a better way to duck type this?
        if hasattr(current_fact, "select"):
          # TODO: Should find a way to categorize here.
          # TODO: Exclude dates.
          # TODO: Exclude citations
          # FIXME: This is very slow - should be a way to do this more concurrently.
          try:
            # FIXME: This is sloppy.
            stripped_url = re.sub(r".+/wiki/", "", current_fact["href"]).replace("/wiki/", "").replace("(", " ").replace(")", " ").replace("_", " ").replace("  ", " ").casefold()
            summary = wikipedia.summary(stripped_url, sentences = 2)
            category = categorize(summary)
            current_set[question_index] = {
              "fact": current_fact.text,
              "summary": summary,
              "category": category 
            }
            fact_links[category].append((base_index, question_index))
          except:
            print("There was an error with retrieving from wikipedia for " + current_fact.text, " aka " + stripped_url)

      fulltext_metadata.append(current_set)

    fact_links_file = open("fact_links.json", "w")
    fact_links_file.truncate(0)
    fact_links_file.write(json.dumps(fact_links))
    fact_links_file.close()

    fulltext_metadata_file = open("fulltext_metadata.json", "w")
    fulltext_metadata_file.truncate(0)
    fulltext_metadata_file.write(json.dumps(fulltext_metadata))
    fulltext_metadata_file.close()

  # Substitute a random2000 link in the writeup for empty spaces.
  question_number = random.randint(0, len(music_facts)-1)
  question = music_facts[question_number]

  # random_fact = random.choice(music_facts)
  answer_fact_number = random.randint(0, len(question.select("a"))-1)
  answer_fact_category = fulltext_metadata[question_number][str(answer_fact_number*2)]["category"]
  false_answers = []
  for _ in range(4):
    location = random.choice(fact_links[answer_fact_category])
    false_answers.append(fulltext_metadata[location[0]][str(location[1])]["fact"])
  
  question.select("a")[answer_fact_number].replace_with("_________________")

  print(question.text)
  print("ANSWER IS " + str(fulltext_metadata[question_number][str(answer_fact_number*2)]))
  print("### FALSE ANSWERS: " + str(false_answers))

main()