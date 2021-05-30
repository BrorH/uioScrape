import argparse
import atexit
import hashlib
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from mounter import *


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_hash_from_file(path):
    # returns a unique utf-8 encoded hash of pdf at given path
    m = hashlib.md5()
    try:
        with open(path, "rb") as file:
            
            m.update( file.read())
    except Exception as e:
        # if the above fails, create a hash from just the filename
        print(e)
        m.update(bytes(str(path).split("/")[-1].encode("utf-8")))
    return m.digest()


def generate_hash_file(dir):
    # generate a hash file from the pdfs within the given dir 
    globber = [str(file) for file in Path(dir).rglob('*.pdf')]
    hash_arr = np.array(["a"*16]*len(globber), dtype=bytes)
    for i,path in enumerate(globber):
        hash_arr[i] = get_hash_from_file(path)
    return hash_arr

def bytesize_to_readable(bytes, failsafe =True):
    #converts a number of bytes to the most appropriate prefix format, i.e k, M, G etc
    if 0 <= bytes < 1e3:
        return f"{bytes} B"
    elif 1e3 <= bytes < 1e6:
        return f"{int(bytes//1e3)} kB"
    elif 1e6 <= bytes < 1e9:
        return f"{int(bytes//1e6)} MB"
    elif 1e9 <= bytes < 1e10:
        return f"{int(bytes//1e9)} GB"
    elif failsafe:
        # add failsafe for files over 10 GB
        print(f"{bcolors.FAIL} Encountered too large file (>50 GB). Exiting. {bcolors.ENDC}")
        unmount_webdav()
        sys.exit()
    return f"{int(bytes//1e9)} GB"

filename_count_re = re.compile(r"([^(]+?)(\(\d+\))?\.pdf", re.IGNORECASE)
def download_subject(subject):
    # starts the downloading process. Also makes sure that no duplicate files are downloaded
    print("Loading... Please wait")
    dl_dir = os.path.abspath("./downloads/"+subject) # dir to be downloaded into
    if not os.path.isdir(dl_dir): # if not dir exists, create it 
        subprocess.run(["mkdir", "-p", dl_dir])

    hash_arr = list(generate_hash_file(dl_dir)) # create an empty hash file and get an empty list of correct length
    mnt_pathglob = list(Path('./.mnt/').rglob('*.pdf'))
    dl_pathglob = list(Path(dl_dir).rglob('*.pdf'))
    dl_pathglob_names = [re.findall(filename_count_re, file.name)[0][0] for file in dl_pathglob] # get names without extension or count number (#)
    num_of_files_found = len(mnt_pathglob)
    bytes_downloaded = 0 # count all bytes downloaded 
    files_downloaded = 0 # count number of downloaded files
    print(f"Found {num_of_files_found} potential pdfs")
    for num,file in enumerate(mnt_pathglob):

        skip = False
        print_suffix = ""
        print_prefix = f"{bcolors.BOLD}({num+1}/{num_of_files_found}){bcolors.ENDC} "
        hashed_file = get_hash_from_file(file)
        
        filename = re.findall(filename_count_re, str(file.name))[0][0]# strip .pdf extension in order to compare count number
        if hashed_file not in hash_arr:
            # if this succeeds, then the pdf is unique and will be downloaded
            for ignore in args.i:
                if ignore in filename.lower(): 
                    print(print_prefix+ f"{bcolors.WARNING} Skipped {bcolors.ENDC} {filename}.pdf: Ignored")
                    skip = True
                    break 
            if skip: continue
                
            if filename in dl_pathglob_names:
                occurances = sum([filename == foo for foo in dl_pathglob_names])
                assert occurances > 0, "I mean, if this gets called, you really fucked up"
                if occurances > 0:
                    downloaded_filename =filename + f"({occurances}).pdf"
                print_suffix = f" {bcolors.OKBLUE}(Added suffix due to existing filename){bcolors.ENDC}"
                
            else:
                downloaded_filename = filename + ".pdf"
            dl_pathglob_names.append(filename)
            
            process = subprocess.Popen(["cp","-p", file, f"{dl_dir}/{downloaded_filename}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            if err:
                print(f"{bcolors.FAIL}{err.decode('utf-8').rstrip()}{bcolors.ENDC}")
                continue
            
            dl_size = os.stat(f"{dl_dir}/{downloaded_filename}").st_size
            
            files_downloaded += 1
            bytes_downloaded += dl_size

            dl_size = bytesize_to_readable(dl_size)
            print(print_prefix + f"{bcolors.OKGREEN}Downloaded{bcolors.ENDC} {downloaded_filename}"+f" ({dl_size})" + print_suffix)
            time.sleep(0.05)
            hash_arr.append(hashed_file)
        else:
            pass
            print(print_prefix + f"{bcolors.WARNING} Skipped {bcolors.ENDC} {filename}.pdf: Duplicate")
    

    print("================================================")
    print(f"   Downloaded {files_downloaded} files for a total of {bytesize_to_readable(bytes_downloaded, failsafe=False)}.")
    print("================================================\n")



def scraper(subject):
    #starts the scraper
    subject = subject.upper()

    # the line below is an abomination which I intend to fix "later"
    subjects_dict = eval(np.load(os.path.relpath("./src/subjects.npy"), allow_pickle=True).__repr__().lstrip("array(").rstrip(",\n      dtype=object)\n"))
    try:
        dav_url = "https://www-dav.uio.no/studier/emner"+subjects_dict[subject]
    except KeyError:
        print(f"Subject '{subject}' not found")
        sys.exit(1)

    init_mountcheck()
    atexit.register(unmount_webdav)
    mount_webdav(dav_url) 
    download_subject(subject)
    atexit.unregister(unmount_webdav)
    unmount_webdav()


parser = argparse.ArgumentParser(description='Scrape all semester pages of a UiO subject in order to get the urls of PDFs of old exams and their solutions.\n Made by Bror Hjemgaard, 2021')
parser.add_argument('SUBJECT', metavar='SUBJECT', nargs=1,
                    help='Subject code of any UiO subject. Case insensitive')
parser.add_argument("-i", metavar="expr",nargs="*", help="Patterns to ignore in filenames, separated by comma, i.e 'lecture,assignment'. Pdfs with names containing these will not be downloaded")
    

if __name__ == '__main__':
    args = parser.parse_args()
    subject = args.SUBJECT[0]
    scraper(subject)
    
