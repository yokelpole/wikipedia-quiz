
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
      " they ",
      " singer",
      " songwriter",
      " activist",
      " bassist",
      " guitarist",
      " musician",
      " director",
      " writer",
      " composer",
      " dancer",
    ],
    "person-male": [
      " man ",
      " he ",
      " his ",
      " actor",
      "husband ",
    ],
    "person-female": [
      " woman ",
      " her ",
      " she ",
      " actress",
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