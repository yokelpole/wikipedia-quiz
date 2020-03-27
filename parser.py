from bs4 import BeautifulSoup
import urllib.request
import wikipedia
import asyncio
import random

def main():
  html = urllib.request.urlopen(wikipedia.page("2000 in music").url).read()
  parsed_html = BeautifulSoup(html, "html.parser")
  
  # On the music summary pages this will grab the "events"
  # that happened for a given year.
  elements = []
  element = parsed_html.select("h2>span[id='Events']")[0].parent
  
  # Only rip data between the two <h2>s
  cut_off_element = element.find_next("h2")

  # FIXME: This can probably be done with a map
  while element != cut_off_element:
    if hasattr(element, "select") == False:
      element = element.next_element
      continue
    if element.select("ul li") and not element.select("ul li ul"):
      elements.extend(element.select("ul li"))
    element = element.next_element

  # Ensure that we have more than one anchor element - anything with less is
  # unlikely to be a quizzable fact.
  music_facts = list(filter(lambda x: len(x.select("a")) > 1, elements))

  # Substitute a random link in the writeup for empty spaces.
  random_fact = random.choice(music_facts)
  random.choice(random_fact.select("a")).replace_with("______________")
  print(random_fact.text)

main()