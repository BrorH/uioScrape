# UiOScrape
> Effortlessly extract exams, exam solutions, lectures, exercises etc. from old lecture pages of any UiO subject.  
> Finds published and unpublished files from the UiO servers. Great for exam studying

## Table of contents
- [Installing](#installing)
  - [Windows](#windows)
  - [MacOS](#macos)
  - [Linux](#linux)
- [Usage](#usage)
  - [scraper.py](#scraperpy)
  - [FAQ](#faq)
    - [*Why does the program ask me to log in with my UiO account?*](#why-does-the-program-ask-me-to-log-in-with-my-uio-account)
    - [*Ummm, ok is there a "no-login" option?*](#ummm-ok-is-there-a-no-login-option)
    - [*Can I get in trouble for using this?*](#can-i-get-in-trouble-for-using-this)
  - [To-do list](#to-do-list)
  - [To-done list](#to-done-list)
  - [Status](#status)
  - [Contact](#contact)


# Installing
## Windows
ahahahaha
## MacOS
pray to GNU and follow [Linux](#linux) guide
## Linux
1. Requires **Python3.8 or later**  as well as `numpy`:
   - `$ pip install numpy`
2. [Clone](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) this repo.  
3. Run `install.sh` as root, i.e  `$ sudo ./install.sh`

<br>  


# Usage
 
## scraper.py
Run the python script and pass any UiO subject as the first and only argument. Example:  
`python3.8 scraper.py FYS-MEK1110`  
The subject code is case-insensitive.  
You will be asked to enter your UiO username and password ([why](#faq)?). You will have to enter these credentials every time you run the scraper.

Run `scraper.py --help` for help.

As of now all pdfs of a given subject are downloaded into a ./downloads dir in the cloned repo. The downloader recognizes and skips duplicate files (even though they might be under different names!). Often several hundred pdfs are identified within each subject and a large part of them are downloaded. This may seem like an intensive and large downloading process, but most pdfs are often less than 1MB, and there are likely very many duplicates. You can halt the downloading at any time by stopping the program. This also safely unmounts the file system.
Future versions will feature more controllable downloading options and more filtering methods.  
It is worth noting that the downloading gets exponentially faster, as the system needs time to finish mounting.   


<!-- ## credentials.py
Running this script and following the instructions will allow you to use a pin-code instead of your UiO credentials every time by encrypting and storing your credentials. If you are the main user of your computer this should not be a problem. However for multi-user systems, this is not recommended. This is similar to the git-credentials approach of achieving seamless login, (which surprisingly just stores your password plaintext!) -->

  

#
### To-do list
- [ ] Add support for other files than just .pdfs
- [ ] Add Windows / MacOS support
- [ ] Add more command line arguments, like max downloads, max size downloads, etc
- [ ] Add autocomplete for all subjects via command line
- [ ] Add smart filter which detects only specific file types (i.e exams or obligs) 
- [ ] Eat 🍕
- [ ] bugsbugsbugs

### To-done list
- [x] Extract files though mounting of UiO webDav server 
- [x] Implement hashing/UUID system to assert no file is downloaded twice. 
- [x] Safer unmounting system
- [x] SaferER unmounting system
- [x] You have to be an idiot to mess up this unmounting system
- [x] Group results in a prettier manner
- [x] Create installation script
    
#
## FAQ
### *Why does the program ask me to log in with my UiO account?*
As a UiO student you are granted access to the course pages of most semester pages of most subjects. Simply telling the UiO servers that you are indeed a student grants you the ability to view and download resources that do not appear publicly on the semester web pages.  
The great thing about open source is that you can confirm for yourself that the scraper does nothing dubious with your credentials.
The usernames/passwords are **never** seen by any of the scripts in this repo. The credentials request happens early in `mounter.py` and you can tweak and check for yourself that the passwords are purely handled by the [wdfs](http://noedler.de/projekte/wdfs/) module. Of course you should _never_ trust your usernames and passwords to untrusted sources, but the fact that this repo exists and UiO has not demolished into oblivion should hint at some degree of legitimacy. You are of course entitled to being careful when it comes to giving up your passwords to unresponsive terminals prompts, but at this point I guess you just have to trust me 😉

### *Ummm, ok is there a "no-login" option?*
Yes, there will eventually be! While not currently fully implemented, there will soon be an option to perform classic web-scraping of the html pages of each semester course. While this scraping allows _anyone_ to scrape for pdfs this method is slow, resource heavy, has **very** ugly code and most importantly *it **can't** find* the above mentioned non-public files (which are often the most juicy ones 😉)

### *Can I get in trouble for using this?*
No. However, common sense applies; don't behave inappropriately and don't be an idiot and everything will be fine. These files are available to all UiO students, this program just quickly and neatly collects them.

### *When will you remove 'Eat 🍕' from the to-do list*?
The day when I wont have to google regex syntaxing, I'll allow myself a slice

  

## Status
Project is: _in development but useable_

## Acknowledgements
This project uses [wdfs](https://github.com/jmesmon/wdfs); a free, open source webdav filesystem. UiOScrape is not officially associated with the University of Oslo, but thanks to UiO for having such a well-documented files-storage system.

## Contact
Created by [Bror Hjemgaard](mailto:bror.hjemgaard@gmail.com) - feel free to contact me!