import hashlib
import sys
import time
import urllib
from urllib.request import urlopen
import argparse
import re 
import getpass 
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path
from sys import platform

unique_pdfs = []
download_size = 0
request_count = 0
download_count = 0
class bcolors:
    if platform == "win32":
        HEADER = ''
        OKBLUE = ''
        OKCYAN = ''
        OKGREEN = ''
        WARNING = ''
        FAIL = ''
        ENDC = ''
        BOLD = ''
        UNDERLINE = ''
    else:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'


def bytesize_to_readable(bytes, failsafe =True):
    #converts a number of bytes to the most appropriate prefix format, i.e k, M, G etc
    if 0 <= bytes < 1e3:
        return f"{bytes} B"
    elif 1e3 <= bytes < 1e6:
        return f"{int(round(bytes/1e3))} kB"
    elif 1e6 <= bytes < 1e9:
        return f"{int(round(bytes/1e6))} MB"
    elif 1e9 <= bytes < 1e10:
        return f"{int(round(bytes/1e9))} GB"
    elif failsafe:
        # add failsafe for files over 10 GB
        print(f"{bcolors.FAIL} Encountered too large file (>50 GB). Exiting. {bcolors.ENDC}")
        sys.exit(1)
    return f"{int(bytes//1e9)} GB"

def download_pdf(url):
    # Does all the pdf validation, hashing and potentially downloads any unique pdfs

    global request_count, download_count, hash_arr, patterns_to_ignore, download_size
    leading_path, filename = tuple(re.findall(get_local_path_re, url)[0])
    path_to_print = f"{leading_path}{bcolors.BOLD}{filename}{bcolors.ENDC}"

    if patterns_to_ignore:
        for pattern in patterns_to_ignore:
            if pattern in filename:
                print(f"{bcolors.WARNING}Skipped{bcolors.ENDC}:    {path_to_print} {bcolors.OKCYAN}(Ignored){bcolors.ENDC}")
                print(f"  {bcolors.BOLD}Downloads{bcolors.ENDC}: {download_count} {bcolors.BOLD}Requests{bcolors.ENDC}: {request_count}\r",end="")
                return


    result = urllib.request.urlopen(url)
    raw_pdf = result.read()
    
    hash = hashlib.md5(raw_pdf).digest()
    print_suffix = ""
    if hash not in hash_arr:
        hash_arr.append(hash)
        if filename in filenames:
            filename_extension_stripped = filename.rstrip(".pdf")
            temp_filename = filename#os.path.join("./downloads",subject,filename)
            counter = 1

            while os.path.exists(os.path.join("./downloads",subject,temp_filename)):
                temp_filename = filename_extension_stripped + "(" + str(counter) + ").pdf"
                counter += 1
            filename = os.path.basename(temp_filename)
            
            path_to_print = f"{leading_path}{bcolors.BOLD}{filename}{bcolors.ENDC}"
            print_suffix = f" {bcolors.OKBLUE}(Added suffix due to existing filename){bcolors.ENDC}"
        else:
            filenames.append(filename)
        with open(os.path.abspath(os.path.join("./downloads",subject,filename)), "wb") as f:
            f.write(raw_pdf)
        download_size += sys.getsizeof(raw_pdf)
        print(f"{bcolors.OKGREEN}Downloaded{bcolors.ENDC}: {path_to_print}, ({bcolors.HEADER}{bytesize_to_readable(sys.getsizeof(raw_pdf))}{bcolors.ENDC})"+print_suffix)
        download_count += 1

        print(f"  {bcolors.BOLD}Downloads{bcolors.ENDC}: {download_count} {bcolors.BOLD}Requests{bcolors.ENDC}: {request_count}\r",end="")
        time.sleep(0.1) 
        return

    else:
        print(f"{bcolors.WARNING}Skipped{bcolors.ENDC}:    {path_to_print} {bcolors.OKCYAN}(Duplicate){bcolors.ENDC}")
    request_count += 1
    print(f"  {bcolors.BOLD}Downloads{bcolors.ENDC}: {download_count} {bcolors.BOLD}Requests{bcolors.ENDC}: {request_count}\r",end="")




def scrape(url, subdirs_found = [], pdfs_found = []):
    global request_count, download_count
    request_count += 1

    time.sleep(0.03)
    
    response = urllib.request.urlopen(url+"?sort-by=name&invert=true")
    soup = BeautifulSoup(response.read(), "html.parser")
    print(f"  {bcolors.BOLD}Downloads{bcolors.ENDC}: {download_count} {bcolors.BOLD}Requests{bcolors.ENDC}: {request_count}\r",end="")
    
    hrefs = soup.find_all("a")
   
    for href in hrefs:
        attrs = href.attrs
        if "title" in attrs.keys():
            if attrs["title"] == "PDF":
                if (attrs["href"]) not in pdfs_found:
                    new_pdf = attrs["href"]
                    pdfs_found.append(new_pdf)
                    download_pdf(new_pdf)
        if href.findChildren():
            try:
                if (attrs["href"]) not in (subdirs_found):
                    new_url = attrs["href"]
                    subdirs_found.append(new_url)
                    children_subdirs_found= scrape(new_url, subdirs_found, pdfs_found)
                    if children_subdirs_found:
                        for new_url in children_subdirs_found:
                            if new_url not in subdirs_found:
                                subdirs_found.append(new_pdf)
            except KeyboardInterrupt:
                print("\n",end="")
                raise KeyboardInterrupt
            except urllib.error.HTTPError:
                continue
    return subdirs_found

def get_subject_path(subject):
    # Called early in program with the terminal argument subject in order to check if its a valid subject and return the path of it
    with open("src/subjects.json", "r+") as file:
        subject_dict = json.load(file)
    try:
        dav_url = "https://www-dav.uio.no"+subject_dict[subject]
    except KeyError:
        print(f"Subject '{subject}' not found")
        sys.exit(1)
    return dav_url

def get_hash_from_file(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).digest()

def init(subject):
    # initializes the scraper. makes sure the correct folders exists. If subject already ahs downloaded files, returns an array of the hashed files as well as the names

    if not os.path.isdir(os.path.abspath("./downloads")):
        # makse sure the ./downloads dir exists
        os.mkdir(os.path.abspath("./downloads"))
    dl_dir = os.path.abspath(os.path.join("./downloads/",subject)) # dir to be downloaded into
    if not os.path.isdir(dl_dir): # if not dir exists, create it 
        os.mkdir(dl_dir)
        return [], []
    else:
        # if subject dir already exists, generate a hash of the pre-existing files
        globber = [str(file) for file in Path(dl_dir).rglob('*.pdf')]
        hash_arr = [get_hash_from_file(path) for path in globber]
        filenames = [os.path.basename(path) for path in globber]
        return hash_arr, filenames


parser = argparse.ArgumentParser(description='Scrape all semester pages of a UiO subject in order to get the urls of PDFs of old exams and their solutions.\n Made by Bror Hjemgaard, 2021')
parser.add_argument('SUBJECT', metavar='SUBJECT', nargs=1,
                    help='Subject code of any UiO subject. Case insensitive')
parser.add_argument("-i", metavar="expr",nargs="*", help="Patterns to ignore in filenames. Pdfs with names containing these will not be downloaded")

parser.add_argument("-s", metavar="sem",nargs="*", help="Which semesters to look for files in, i.e H16, S21 (or V21 for the norwegians). Single digit-years must be zero-left padded. Case insensitive")
parser.add_argument("-f", metavar="expr", nargs = "*", help="NOT IMPLEMENTED: Only download files which match these expressions")
parser.add_argument("--ignore-subject-files",  action="store_true", help="NOT IMPLEMENTED: If passed, ignores files which are not under any semester; aka subject-wide files")



if __name__ == "__main__":
    args = parser.parse_args()
    subject = args.SUBJECT[0].upper()
    get_local_path_re = re.compile(r"https:\/\/www-dav.uio.no\/studier\/emner\/(?:.+?\/)+?"+subject+r"\/(.+\/)(.*)",re.IGNORECASE)

    patterns_to_ignore = args.i 
    semesters_to_scrape = args.s
    base_url = get_subject_path(subject)
    hash_arr, filenames = init(subject)


    # setup auth manager
    print("Enter UiO Username")
    user = input(">> ")
    print("Enter Password (Check README if you wonder why you have to provide UiO credentials)")
    pwd = getpass.getpass(">> ")
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, base_url, user, pwd)
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)
    urllib.request.install_opener(opener)

    print(f"Scraping {subject}:")
    start_time = time.time()
    scrape(base_url)
    

    print(f"\n=========================\nDownloaded {download_count} pdfs ({bytesize_to_readable(download_size)}) in {round(time.time()-start_time,1)} seconds")
    

    
