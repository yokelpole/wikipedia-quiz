
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
  - Will probably have to make use of a HTML parsing library as well, as the 