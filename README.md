# UiOScrape
> Effortlessly extract exams, exam solutions, lectures, exercises etc. from old lecture pages of any UiO subject.

## Table of contents
- [UiOScrape](#uioscrape)
  - [Table of contents](#table-of-contents)
  - [General info](#general-info)
  - [Technologies](#technologies)
- [Installing](#installing)
  - [Windows](#windows)
  - [MacOS](#macos)
  - [Linux](#linux)
- [Usage](#usage)
  - [scraper.py](#scraperpy)
  - [credentials.py](#credentialspy)
  - [Features](#features)
    - [To-do list:](#to-do-list)
    - [To-done list:](#to-done-list)
  - [FAQ](#faq)
    - [*Why does the program ask me to log in with my UiO account?*](#why-does-the-program-ask-me-to-log-in-with-my-uio-account)
    - [*Ummm, ok is there a "no-login" option?*](#ummm-ok-is-there-a-no-login-option)
    - [*Can I get in trouble for using this?*](#can-i-get-in-trouble-for-using-this)
    - [*When will you eat 🍕*?](#when-will-you-eat-)
  - [Status](#status)
  - [Contact](#contact)

## General info
Add more general information about project. What the purpose of the project is? Motivation?


## Technologies
* Tech 1 - version 1.0
* Tech 2 - version 2.0
* Tech 3 - version 3.0

# Installing
## Windows
ahahahaha
## MacOS
pray to GNU and follow [Linux](#Linux) guide
## Linux
Requires **Python3.8 or later**  as well as the modules
- numpy:  `$ pip install numpy`
- cryptography: `$ pip install cryptography`   

Requires [wdfs](https://github.com/jmesmon/wdfs) (1.4.2 or later):  
**HOW TO INSTALL WDFS**:  
(tutorial kindly stolen verbatim from [Khurshid Alam](https://askubuntu.com/questions/254241/gnote-tomboy-webdav-connecting-error) on askubuntu.com)

`sudo apt-get install checkinstall libfuse-dev libneon27 libneon27-dev`
`sudo apt-get install python-fuse fuse-utils`

`wget http://noedler.de/projekte/wdfs/wdfs-1.4.2.tar.gz`
`tar xzvf wdfs-1.4.2.tar.gz`
`cd wdfs-1.4.2`
`./configure`\
`sudo checkinstall`
`sudo dpkg -i wdfs_1.4.2-1_*.deb`

[Clone](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) the repo. 


# Usage
## scraper.py
Show examples of usage:
`put-your-code-here`


## credentials.py


## Features
List of features ready and TODOs for future development
* Awesome feature 1
* Awesome feature 2
* Awesome feature 3
  

#
### To-do list:
- [ ] Add support for other files than just .pdfs
- [ ] Come up with some genius, Apple Inc. level idea
- [ ] a
- [ ] Add smart filter which detects only specific file types (i.e exams or oblig) 
- [ ] Group results in a prettier manner
- [ ] Eat 🍕

### To-done list:
- [x] Extract files though mounting of UiO webDav server
- [x] Basic password/pin system for credential storage 
- [x] Implement hashing/UUID system to assert no file is downloaded twice. 
#
## FAQ
### *Why does the program ask me to log in with my UiO account?*
As a UiO student you are granted access to the course pages of most semester pages of most subjects. Simply telling the UiO servers that you are indeed a student grants you the ability to view and download resources that do not appear publicly on the semester web pages.

### *Ummm, ok is there a "no-login" option?*
Yes! While not currently fully implemented, there will soon be an option to perform classic web-scraping of the html pages of each semester course. While this scraping allows _anyone_ to scrape for pdfs this method is slow, resource heavy, has **very** ugly code and most importantly *it **can't** find* the above mentioned non-public files (which are often the most juicy ones 😉)

### *Can I get in trouble for using this?*
No. However, common sense applies; dont behave inappropriately or be an idiot and everything will be fine. These files are available to all UiO students, this program just quickly and neatly collects them.

### *When will you eat 🍕*?
The day when I wont have to google regex syntaxing, I'll allow myself a slice

  

## Status
Project is: _heavily in development_


## Contact
Created by [Bror Hjemgaard](mailto:bror.hjemgaard@gmail.com) - feel free to contact me!