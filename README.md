A Python framework for generating quizzes based off of lists in Wikipedia articles. Uses scikit-learn to categorize answers into different categories so that they can be presented in a multiple-choice list.

# Installing:
- Clone this repo
- Install `BeautifulSoup4`, `sklearn`, `nltk` via `pip3`. (There are a few more dependencies that I haven't listed here - you'll have to install them as you attempt to run the scripts, sorry!)
- Use the tools below

# Tools:

## train.py
Used to train and generate the model used by `crawler.py`. Makes use of the data in `data` to generate a model. Data in `data` is classified according to the directory it is in. 

Provides details about the model test results when run and saves the new model into `trained_model*.pickle` files.

*Usage:* `python3 train.py`

## crawler.py
Targets and crawl a section of a Wikipedia page, turning the bullet points in that section into quiz questions and answers. It targets from one `<h2>` element on the page to the next, as that is a relatively common way to break Wikipedia pages into separate sections.

*Usage:* `python3 crawler.py <page name> <h2 ID of section>`
*Example:* `python3 crawler.py "2004 in music" "Popular_songs"`

## quiz.py
Provides a way to test the question and answer functionality in the terminal. A specific question set can be provided for one-off testing, otherwise all quiz data available in `quiz_content` is used to provide 5 questions to the user.

*Usage:* `python3 quiz.py`
*Example:* `python3 quiz.py "2004 in music" "Popular_songs"`

## websocket_server.py
Used to serve and keep track of game state for the [wikipedia-quiz-client](https://github.com/yokelpole/wikipedia-quiz-client).

*Usage:* `python3 websocket_server.py`
