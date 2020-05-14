from nltk.stem import WordNetLemmatizer
import re

def get_html_questions(html, start_header_text):
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

    for current_element in element.select("li"):
      # FIXME: This should probably be recursive to super nested lists.
      if current_element.select("ul li"):
        elements.extend(current_element.select("li"))
      else:
        elements.append(current_element)
        
    element = element.next_element

  return elements 

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
    # Do we really need the <li>? 
    if element.select("li a[title]"):
      elements.extend(element.select("li a[title]"))
    element = element.next_element

  return elements

def lemmatizer(X):
    stemmer = WordNetLemmatizer()
    documents = []
    for sen in range(0, len(X)):
        # Remove all the special characters
        document = re.sub(r'\W', ' ', str(X[sen]))
        # remove all single characters
        document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)
        # Remove single characters from the start
        document = re.sub(r'\^[a-zA-Z]\s+', ' ', document) 
        # Substituting multiple spaces with single space
        document = re.sub(r'\s+', ' ', document, flags=re.I)
        # Removing prefixed 'b'
        document = re.sub(r'^b\s+', '', document)
        # Converting to Lowercase
        document = document.lower()
        # Lemmatization
        document = document.split()
        document = [stemmer.lemmatize(word) for word in document]
        document = ' '.join(document)
        documents.append(document)
    return documents
