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
