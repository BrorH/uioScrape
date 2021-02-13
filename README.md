# UiOScrape
Retrieve exams and solutions from any matnat subject by the press of a button.
Scrapes all semester pages of a matnat subject and smartly finds pdf's of old exams and (similar files). 
Is programmed to not overload or cause strain on the UiO servers in any manner, but use at your own risk and do not tweak the code too much if you do not know how to use it.
Still an early version and bugs should be expected.
The search can be stopped at any time by pressing ctrl+C.

## Requriements:
* python3.8 or higher
* numpy
* wdfs

### How to installl wdfs

sudo apt-get install checkinstall libfuse-dev libneon27 libneon27-dev
sudo apt-get install python-fuse fuse-utils

wget http://noedler.de/projekte/wdfs/wdfs-1.4.2.tar.gz
tar xzvf wdfs-1.4.2.tar.gz
cd wdfs-1.4.2
./configure
sudo checkinstall
sudo dpkg -i wdfs_1.4.2-1_*.deb


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
- [ ] improve "priority"-evaulation so as to completely remove urls/pdfs with uninteresting names
- [x] add auto-download option
- [ ] add wider command-line argument support
- [x] add a request-throttle so as to prevent stress on uio server
- [x] dont download already-downloaded pdfs and add uuid system to separate files of same names
- [x] put everything into a class
- [ ] print result in a prettier manner. Collect exams by semester and print pairwise (if possible)
- [ ] eat pizza
- [ ] add warning messages if user inputs parameters that may cause a high load on the servers
- [ ] overall polishing

