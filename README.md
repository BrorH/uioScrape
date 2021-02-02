# UiOScrape
Retrieve exams and solutions from any matnat subject by the press of a button.
Scrapes all semester pages of a matnat subject and smartly finds pdf's of old exams and (similar files). 
Is programmed to not overload or cause strain on the UiO servers in any manner, but use at your own risk and do not tweak the code too much if you do not know how to use it.
Still an early version and bugs should be expected.
The search can be stopped at any time by pressing ctrl+C.

## Requriements:
* python3.8 or higher
* urllib, ratelimit, argparse, multiprocessing, numpy (let me know if I'm missing any)
## Usage:
`python3 main.py subject`


## todo
- [ ] support other faculties than just matnat
- [ ] support retrieving other files than just exams, like lectures, messages, formula sheets, all .txt/.py files, etc. 
- [x] faster search
    - [x] threading (can be further improved)
    - [x] Only some areas of the website will contain potential interesting links
    - [x] Some links are commonly uninteresting across all semester page
- [x] add smarter pdf-quality check.
- [x] add option for quality pdf check
- [ ] add auto-download option
- [x] add wider command-line argument support
- [x] add a request-throttle so as to prevent stress on uio server
- [ ] store links in cache
- [ ] store light version of semester websites in cachce and compare to current. Re-run scraper if versions do not match
- [x] put everything into a class
- [ ] print result in a prettier manner. Collect exams by semester and print pairwise (if possible)
- [ ] eat pizza
- [ ] add warning messages if user inputs parameters that may cause a high load on the servers

