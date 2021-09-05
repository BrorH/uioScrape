# UiOScrape
> Scrape the UiO servers for visible and hidden files. Effortlessly finds exams, exam solutions, lectures exercises etc. 
> Great for exam studying or finding solutions to exercises

## Contents
- [UiOScrape](#uioscrape)
  - [Contents](#contents)
- [Installing](#installing)
- [Usage](#usage)
  - [scraper.py](#scraperpy)
- [Features](#features)
    - [To-do list](#to-do-list)
    - [To-done list](#to-done-list)
- [FAQ](#faq)
    - [*Why does the program ask me to log in with my UiO account?*](#why-does-the-program-ask-me-to-log-in-with-my-uio-account)
    - [*Can I get in trouble for using this?*](#can-i-get-in-trouble-for-using-this)
# Installing
1. Requires **Python3** as well as the module [bs4](https://pypi.org/project/beautifulsoup4/):
    
    `pip install bs4`
2. [Clone](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) this repo:

    `git clone https://www.github.com/BrorH/UiOScrape.git`

<br>  


# Usage
 
## scraper.py
Main script. Pass any UiO subject in order to start the scraping. Example:
`python3.8 scraper.py FYS-MEK1110`. The subject code is case-insensitive.  
You will be asked to enter your UiO username and password ([why](#faq)?). You will have to enter these credentials every time you run the scraper.
The scraped files will be downloaded into a folder `downloads` within the `UiOScrape` directory which will be created the first time you run the scraper. In the example above, all files will be downloaded into the directory `./downloads/FYS-MEK1110`. 

Run `scraper.py --help` for help.


# Features
- Smart downloading which assures that duplicate files won't be downloaded (even though they may have different filenames).
- If two or more files have different content but same name, an appropriate filename suffix is constructed, e.g `file.pdf` and `file(1).pdf`
- Ignore certain patterns within the filenames.


### To-do list
- [ ] Add support for other files than just pdfs
- [ ] Add more command line arguments, like max downloads, max size downloads, etc
- [ ] Add autocomplete for all subjects via command line
- [ ] Add smart filter which detects only specific file types (i.e exams or obligs) 
- [ ] bugsbugsbugs

### To-done list
- [x] Add Windows / MacOS support
- [x] Revamp entire scraping system to be reliant on requests rather than mounting
- [x] Implement hashing/UUID system to assert no file is downloaded twice. 
- [x] Group results in a prettier manner
- [x] Eat 🍕
- [x] ~~Extract files though mounting of UiO webDav server~~
- [x] ~~Safer unmounting system~~
- [x] ~~Create installation script~~
    

# FAQ
### *Why does the program ask me to log in with my UiO account?*
As a UiO student you are granted access to the course pages of most semester pages of most subjects. Simply telling the UiO servers that you are indeed a student grants you the ability to view and download resources that do not appear publicly on the semester web pages. The script scrapes websites like [this](https://www-dav.uio.no/studier/emner/matnat/fys/FYS1001/), which requires authentication. In order to adhere to UiO's [IT Rules](https://www.uio.no/english/about/regulations/it/) you will have to provide credentials every time.

The great thing about open source is that you can confirm for yourself that the scraper does nothing dubious with your credentials.
Your password is handled by the `getpass` module and is only used once to create an [HTTP authentication manager](https://docs.python-requests.org/en/master/user/authentication/). If you have any concerns, please [contact me](mailto:bror.hjemgaard@gmail.com).


### *Can I get in trouble for using this?*
No. However, netiquette applies; don't behave inappropriately and don't be an idiot and everything will be fine. These files are available to all UiO students, this program just quickly and neatly collects them. The scraper is built with UiO's [IT Rules](https://www.uio.no/english/about/regulations/it/) in mind, meaning as long as you don't deliberately _try_ to annoy the servers, you will be ok.


  