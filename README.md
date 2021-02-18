# UiOScrape
> Effortlessly extract exams, exam solutions, lectures, exercises etc. from old lecture pages of any UiO subject.  
> Finds unpublished files from the UiO servers. Great for exam studying

## Table of contents
- [UiOScrape](#uioscrape)
  - [Table of contents](#table-of-contents)
- [Installing](#installing)
  - [Windows](#windows)
  - [MacOS](#macos)
  - [Linux](#linux)
      - [HOW TO INSTALL WDFS:](#how-to-install-wdfs)
- [Usage](#usage)
  - [scraper.py](#scraperpy)
  - [credentials.py](#credentialspy)
    - [To-do list:](#to-do-list)
    - [To-done list:](#to-done-list)
  - [FAQ](#faq)
    - [*Why does the program ask me to log in with my UiO account?*](#why-does-the-program-ask-me-to-log-in-with-my-uio-account)
    - [*Ummm, ok is there a "no-login" option?*](#ummm-ok-is-there-a-no-login-option)
    - [*Can I get in trouble for using this?*](#can-i-get-in-trouble-for-using-this)
    - [*When will you eat 🍕*?](#when-will-you-eat-)
  - [Status](#status)
  - [Contact](#contact)


# Installing
## Windows
ahahahaha
## MacOS
pray to GNU and follow [Linux](#linux) guide
## Linux
1. Requires **Python3.8 or later**  as well as the modules
   - numpy:  `$ pip install numpy`
   - cryptography: `$ pip install cryptography`   

2. [Install wdfs](#how-to-install-wdfs)
3. [Clone](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) the repo.  

<br>  

#### HOW TO INSTALL WDFS:  
[wdfs](https://github.com/jmesmon/wdfs) is a Web-Dav filesharing system required by UiOScrape to work:  
(tutorial kindly stolen verbatim from [Khurshid Alam](https://askubuntu.com/questions/254241/gnote-tomboy-webdav-connecting-error))

`sudo apt-get install checkinstall libfuse-dev libneon27 libneon27-dev`\
`sudo apt-get install python-fuse fuse-utils`

`wget http://noedler.de/projekte/wdfs/wdfs-1.4.2.tar.gz`\
`tar xzvf wdfs-1.4.2.tar.gz`\
`cd wdfs-1.4.2`\
`./configure`\
`sudo checkinstall`\
`sudo dpkg -i wdfs_1.4.2-1_*.deb`






# Usage
 
## scraper.py
Run the python script and pass any UiO subject as the first and only argument. Example:  
`python3.8 scaper.py FYS-MEK1110`  
The subject code is case-insensitive.  
You will be asked to enter your UiO username and password ([why](#faq)?). You will have to enter these credentials everytime you run the scraper, unless you setup a pin-code. See [credentials.py](#credentialspy).  
As of now (almost) all pdfs are downloaded into a ./downloads dir in the cloned repo. Future versions will feature more controllable downloading options and filtering methods.  
It is worth noting that the downloading gets exponentially faster, as the system needs time to finish mounting.   
NOTE: When stopping the program mid-scrape, plese only press "ctrl+C" (or equivalent) __one time__ only, as the program needs to safely unmount after a scrape.
If you did not do this, the program will automatically clean up after you next time you run it, but it may cause some issues (nothing serious) if you act careless



## credentials.py
Running this script and following the instructions will allow you to use a pin-code instead of your UiO credentials every time by encrypting and storing your credentials. If you are the main user of your computer this should not be a problem. However for multi-user systems, this is not recommended. This is similar to the git-credentials approach of achieving seemless login, (which surprisingly just stores your password plaintext!)

  

#
### To-do list:
- [ ] Add support for other files than just .pdfs
- [ ] Add autocomplete for all subjects via command line
- [ ] Chose which files from a scrape to be downloaded
- [ ] Download specific files only
- [ ] Add smart filter which detects only specific file types (i.e exams or oblig) 
- [ ] Eat 🍕
- [ ] Group results in a prettier manner
- [ ] bugsbugsbugs

### To-done list:
- [x] Extract files though mounting of UiO webDav server
- [x] Basic password/pin system for credential storage 
- [x] Implement hashing/UUID system to assert no file is downloaded twice. 
- [x] Safer unmouting system
    
#
## FAQ
### *Why does the program ask me to log in with my UiO account?*
As a UiO student you are granted access to the course pages of most semester pages of most subjects. Simply telling the UiO servers that you are indeed a student grants you the ability to view and download resources that do not appear publicly on the semester web pages.  
The great thing about open source is that you can confirm for yourself that the scraper does nothing dubious with your credentials.

### *Ummm, ok is there a "no-login" option?*
Yes! While not currently fully implemented, there will soon be an option to perform classic web-scraping of the html pages of each semester course. While this scraping allows _anyone_ to scrape for pdfs this method is slow, resource heavy, has **very** ugly code and most importantly *it **can't** find* the above mentioned non-public files (which are often the most juicy ones 😉)

### *Can I get in trouble for using this?*
No. However, common sense applies; don't behave inappropriately and don't be an idiot and everything will be fine. These files are available to all UiO students, this program just quickly and neatly collects them.

### *When will you eat 🍕*?
The day when I wont have to google regex syntaxing, I'll allow myself a slice

  

## Status
Project is: _heavily in development_


## Contact
Created by [Bror Hjemgaard](mailto:bror.hjemgaard@gmail.com) - feel free to contact me!