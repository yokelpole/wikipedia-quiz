import numpy as np 
import re
import nltk
from sklearn.datasets import load_files
import pickle
from nltk.corpus import stopwords
import wikipedia
from nltk.stem import WordNetLemmatizer

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

data = load_files("data")
X, y = data.data, data.target

documents = lemmatizer(X)

from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer(max_features=400, max_df=0.8, strip_accents="unicode", stop_words=stopwords.words('english'))
X = vectorizer.fit_transform(documents).toarray()

from sklearn.feature_extraction.text import TfidfTransformer
tfidfconverter = TfidfTransformer()
X = tfidfconverter.fit_transform(X).toarray()

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

from sklearn.ensemble import RandomForestClassifier
classifier = RandomForestClassifier(random_state=0, bootstrap=False, n_jobs=-1)
classifier.fit(X_train, y_train) 
y_pred = classifier.predict(X_test)

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
print("### RANDOM FOREST")
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
print(accuracy_score(y_test, y_pred))

model_filename = "trained_model.pickle"
pickle.dump(classifier, open(model_filename, "wb"))
model_data_filename = "trained_model_data.pickle"
pickle.dump(data, open(model_data_filename, "wb"))
print("Model saved as " + model_filename + " and " + model_data_filename)
print("### Run crawler.py to make use of this model")
