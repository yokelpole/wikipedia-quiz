
## How will it work?
- Scrape wikipedia pages.
  - Use the `table.infobox` at the top of articles for relatable information.
  - Use the `table.navbox-inner` at the bottom of articles to find further details about the subject.
  - `<h2>` appear to be for the subheadings on pages.
- Start out with just music to keep scope lower.
  - Good candidate to start with and expand with would be the "xxxx in music" pages.
  - Could extract names from bullet points and present a 'fill in the blank' that retrieves several other names from the page.
- Could be fun to do this in Python - Godot Script was very Python like.
  - There is the Python Wikipedia library.
    - `Summary` function could be handy for extra information on links on pages.
  - Pywikibot appears to be a more full-featured library.
  - Will probably have to make use of a HTML parsing library as well
    - Using BeautifulSoup 4

## TODO:
  [] Categorize names, albums, places, and events.
    - Categorization could solve for problem with picking weird links. If something does not have multiple entries then don't show it.
      - Wikipedia's categories don't appear to be very helpful for this...
      - For the "Events" section there seem to be the following:
        - Place
          - First sentence: located in, city, university, in *Capitalized*, 
        - Person
          - First sentence: woman, man, he, she, they, singer, actress, *profession*, singer-songwriter, activist, guitarist, drummer, bassist, musician, 
        - Band
          - First sentence: band, artist, group 
        - Song
          - First sentence: song, composition
        - Album
          - First sentence: album
        - Genre
          - First sentence: genre
        - Event
        - Date
          - First sentence: 'is the xth day of the year' 
        - Award
          - First sentence: award
    - Will need to store where a answer belongs on the question array.
    - How do we store the questions of the same category?
      - Separate category dictionary might be helpful - defines where in the `fact_links` category answers of the same category are defined.
        - Fact links: { "place": [( music_fact_number, array_pos )], "person: [(music_fact_number, array_pos)]}
  [] Allow the user to guess?
  [] Don't select links that are to references and dates at the start of the sentence.
  [] 