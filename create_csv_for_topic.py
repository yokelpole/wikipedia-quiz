import os

csv_file = open("data.csv", "w")
csv_file.truncate(0)

data_folders = os.listdir("data")
for folder_name in data_folders:
  files = os.listdir("data/" + folder_name)
  for file_name in files:
    input_file = open("data/" + folder_name + "/" + file_name, "r")
    line = input_file.readline()
    if len(line) > 0:
      csv_file.write(line.replace(",", "").replace("\n","") + "," + folder_name.upper() + "\n")

csv_file.close()
input_file.close()