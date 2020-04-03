import numpy as np
import re
import nltk
from sklearn.datasets import load_files
nltk.download('stopwords')
import wikipedia
import pickle
from nltk.corpus import stopwords

trivia_data = load_files(r"data")
X, y = trivia_data.data, trivia_data.target

documents = []

from nltk.stem import WordNetLemmatizer
stemmer = WordNetLemmatizer()

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

from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer(max_features=1500, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))
X = vectorizer.fit_transform(documents).toarray()

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=0)

print("TRAIN")

from sklearn.ensemble import RandomForestClassifier
classifier = RandomForestClassifier(n_estimators=1000, random_state=0)
classifier.fit(X_train, y_train)
y_pred = classifier.predict(X_test)

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
print(accuracy_score(y_test, y_pred))

docs_new = [wikipedia.summary("Bob Dylan", sentences=2), wikipedia.summary("Dark Side of the Moon (album)", sentences=2)]

from sklearn.feature_extraction.text import TfidfTransformer
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train)
print(docs_new)
X_new_counts = vectorizer.transform(docs_new)
X_new_tfidf = tfidf_transformer.transform(X_new_counts)
predicted = classifier.predict(X_new_tfidf)

print(predicted)

for doc, category in zip(docs_new, predicted):
  print('%r => %s' % (doc, X.target_names[category]))