import sys
import pickle
import json
import wikipedia
import re

from shared import get_html_facts, lemmatizer
from urllib import request
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

if len(sys.argv) < 3:
  print("Not enough parameters specified.\n Intended use: 'parser.py [topic] [header_text]'")

topic = sys.argv[1].replace(" ", "_")
section = sys.argv[2]

def get_and_save_html(topic):
  # TODO: We should save the output of the HTML as well to ensure it syncs up
  # with fact_links and fulltext_metadata.
  print("### " + topic + " does not exist - fetching data")
  html = request.urlopen(wikipedia.page(topic).url).read().decode("utf-8")
  parsed_html = BeautifulSoup(html, "html.parser")
  
  html_file = open("quiz_content/" + topic + "_page.html", "w")
  html_file.truncate(0)
  html_file.write(html)
  html_file.close()

  return parsed_html

def get_facts_and_metadata_from_html(html, topic, section):
  classifier = pickle.load(open("trained_model.pickle", "rb"))
  classifier_data = pickle.load(open("trained_model_data.pickle", "rb"))  

  from sklearn.feature_extraction.text import TfidfVectorizer
  vectorizer = TfidfVectorizer (min_df=7, max_df=0.8, stop_words=stopwords.words('english'))
  X = vectorizer.fit_transform(lemmatizer(classifier_data.data)).toarray()

  tfidfconverter = TfidfTransformer()
  tfidfconverter.fit_transform(X)

  html_facts = get_html_facts(html, section)
  fact_links = {}
  fulltext_metadata = []

  for base_index, facts in enumerate(html_facts):
    current_set = []
    for current_fact in facts:
      # FIXME: Is there a better way to duck type this?
      if not hasattr(current_fact, "select") or not current_fact.get("title", False):
        continue
      
      if current_fact.get("title", False):
        title = current_fact.get("title")
      else:
        title = current_fact.find_all(title=True)[0].get("title") 

      try:
        print("### CURRENT FACT:")
        print(current_fact)

        title = current_fact.get("title") or current_fact.find_all(title=True)[0]["title"]
        print(title)
        print("### TITLE: " + title)
        summary = wikipedia.summary(title, sentences = 3, auto_suggest=False)

        # Transform the string data into machine learning friendly format
        new_X = vectorizer.transform(lemmatizer([summary])).toarray()
        new_X = tfidfconverter.transform(new_X).toarray()
        results = classifier.predict(new_X)
        category = classifier_data.target_names[results[0]]
        confidence = classifier.predict_proba(new_X)[0][results[0]]

        current_set.append({
          "fact": current_fact.text,
          "summary": summary,
          "category": category,
          "confidence": confidence,
        })
        print(current_set[len(current_set)-1])

        # TODO: Boot out answers that have too low of a confidence score?
        # Or save them into the set metadata and let the quiz deal with it.
        fact_data_file = open("./unsorted_data/" + category + "/" + title + "_fact_data.txt", "w")
        fact_data_file.truncate(0)
        fact_data_file.write(summary)
        if category not in fact_links:
          fact_links[category] = []
        fact_links[category].append((base_index, len(current_set)-1))
      except Exception as e:
        current_set.append(False)
        print("### ERROR: There was an error with retrieving from wikipedia for " + current_fact.text, " aka " + title)
        print(current_fact)
        print(e)
        print(type(e))
        print(e.args)

    fulltext_metadata.append(current_set)

  fact_links_file = open("quiz_content/" + topic + "_" + section + "_fact_links.json", "w")
  fact_links_file.truncate(0)
  fact_links_file.write(json.dumps(fact_links))
  fact_links_file.close()

  fulltext_metadata_file = open("quiz_content/" + topic + "_" + section + "_fulltext_metadata.json", "w")
  fulltext_metadata_file.truncate(0)
  fulltext_metadata_file.write(json.dumps({
    "topic": topic,
    "section": section, 
    "facts": fulltext_metadata
  }))
  fulltext_metadata_file.close()

html = get_and_save_html(topic)
get_facts_and_metadata_from_html(html, topic, section) 
print("### Successfully saved quiz data")
