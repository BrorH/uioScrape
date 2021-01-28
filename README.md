# UiOScrape
Retrieve old exams and solutions from anyy subject by the press of a button

## Requriements:
* python3.8 or higher
* urllib, eventlet
## Usage:
python3 main.py subject

## NOTE
currently only works with fys-subjects
It is not currently very optimized, but it works (barely)
Stop the search any time by pressing ctrl+C
Please use with care so as to not overload the UiO servers :)

## todo
- support other faculties than just matnat
- support retrieving other files than just exams, like lectures, messages, formula sheets, all .txt/.py files, etc. 
- faster search
    - Only some areas of the website will contain potential interesting links
    - Some links are commonly uninteresting across all semester page
- add smarter pdf-quality check. i.e only check response status if pdf seems to be an exam
- add auto-download option
- add wider command-line argument support
- add a request-throttle so as to prevent stress on uio server
- store links in cache
- store light version of semester websites in cachce and compare to current. Re-run scraper if versions do not match
- put everything into a class -

