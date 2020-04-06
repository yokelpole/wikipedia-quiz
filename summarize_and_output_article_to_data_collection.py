import wikipedia
import os
import sys

if sys.argv[1] and sys.argv[2]:
  article = sys.argv[1]
  classification = sys.argv[2]
  summary = wikipedia.summary(sys.argv[1], sentences=2)

  print("### SUMMARY: " + summary)

  filename = "./data/" + classification + "/" + article.replace(" ", "_") + "_fact_data.txt"
  fact_data_file = open(filename, "w")
  fact_data_file.truncate(0)
  fact_data_file.write(summary)
  fact_data_file.close()

  print("Saved as " + filename)
else:
  print("Need both article name and classification as parameters")
