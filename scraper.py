#!/usr/bin/python3
import argparse
import atexit
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from mounter import Mounter


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
    file_hash = hashlib.md5()
    t = 0
    try:
        with open(path, "rb") as f:
            while (chunk := f.read(8192*16)) and t<=100:
                t += 1
                file_hash.update(chunk)

    except OSError:
        # some files are restricted
        return
    return file_hash.digest()
    


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
        Mounter.unmount_webdav()
        sys.exit()
    return f"{int(bytes//1e9)} GB"

def file_with_suffix_constructor(filename, downloaded_filenames):
    # If a filename is already taken, constructs and returns an appropriate name with new suffix

    occurances = sum([filename == foo for foo in downloaded_filenames])
    assert occurances > 0, "I mean, if this gets called, you really fucked up"
    if occurances > 0:
        new_filename =filename + f"({occurances}).pdf"
    return new_filename

def check_if_ignored(filename):
    # if any patterns are to be ignored, they will be checked for here. True if ignored
    if passed_ignore_patterns is None: return False # if no ignores have been given, file will not be ignored
    for ignore in passed_ignore_patterns:
        if ignore in filename.lower(): 
            return True
    return False




filename_count_re = re.compile(r"([^(]+?)(\(\d+\))?\.pdf", re.IGNORECASE)
semester_re = re.compile(r"\.mnt/(?:.+?/)+?([hv]\d\d)(?:.+?)+?\.pdf", re.IGNORECASE)
def download_subject(subject, path_prefix):
    # starts the downloading process. Also makes sure that no duplicate files are downloaded
    print("Loading... Please wait")
    dl_dir = os.path.abspath("./downloads/"+subject) # dir to be downloaded into
    if not os.path.isdir(dl_dir): # if not dir exists, create it 
        subprocess.run(["mkdir", "-p", dl_dir])

    hash_arr = list(generate_hash_file(dl_dir)) # create an empty hash file and get an empty list of correct length

    # if a list of semesters are given, we only wish to study certain directories
    if semesters:
        mnt_pathglob = []
        for sem in semesters:
            mnt_pathglob += list(Path('./.mnt/'+path_prefix+"/"+sem).rglob('*.pdf'))
    else:
        mnt_pathglob = list(Path('./.mnt/'+path_prefix).rglob('*.pdf'))
    
    # order paths by semesters, most recent semesters first
    corresponding_years = []
    for path in mnt_pathglob:
        try:
            semester =  re.findall(semester_re, str(path))[0]
            yr = int(semester[1:])
            if yr > 80:
                yr += 1900
            else:
                yr += 2000
            season = semester[0].lower()
            if season == "h":
                yr += 0.5
        except:
            yr = 9000
        corresponding_years.append(yr)
    mnt_pathglob = [x for _,x in sorted(zip(corresponding_years,mnt_pathglob))][::-1]

    dl_pathglob = list(Path(dl_dir).rglob('*.pdf'))
    dl_pathglob_names = [re.findall(filename_count_re, file.name)[0][0] for file in dl_pathglob] # get names without extension or count number (#)
    num_of_files_found = len(mnt_pathglob)
    bytes_downloaded = 0 # count all bytes downloaded 
    files_downloaded = 0 # count number of downloaded files
    print(f"Found {num_of_files_found} potential pdfs")
    for num,file in enumerate(mnt_pathglob):
        
        try:
            semester = re.findall(semester_re, str(file))[0]

        except:
            
            semester = "--"
        print_prefix = f"{bcolors.BOLD}({num+1}/{num_of_files_found}){bcolors.ENDC} {semester} "
        print_suffix = ""
        print(print_prefix + f"{bcolors.OKCYAN} Loading {bcolors.ENDC}"+ "\r", end="")

        hashed_file = get_hash_from_file(file)#hashfile(file, sample_size=10, sample_threshhold=1000)
        if hashed_file is None:
            # hash may fail if file has restricted access
            print(print_prefix + f"{bcolors.FAIL} Denied{bcolors.ENDC}  {file}: Skipping")
        filename = re.findall(filename_count_re, str(file.name))[0][0]# strip .pdf extension in order to compare count number

        if hashed_file not in hash_arr:
            # if this succeeds, then the pdf is unique and will be downloaded
            
            # check ignores
            if check_if_ignored(filename):
                print(print_prefix+ f"{bcolors.WARNING} Skipped {bcolors.ENDC} {filename}.pdf: Ignored")
                continue
            
            # check if filename already exists
            if filename in dl_pathglob_names:
                new_filename = file_with_suffix_constructor(filename, dl_pathglob_names)
                print_suffix = f" {bcolors.OKBLUE}(Added suffix due to existing filename){bcolors.ENDC}"
            else:
                new_filename = filename + ".pdf"

            # add the found file to the glob
            dl_pathglob_names.append(filename)

            print(print_prefix + f"{bcolors.OKCYAN}Downloading {bcolors.ENDC} {new_filename}"+ "\r", end="")
            # time.sleep(1)
            process = subprocess.Popen(["cp","-p", file, f"{dl_dir}/{new_filename}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            if err:
                print(f"{bcolors.FAIL}{err.decode('utf-8').rstrip()}{bcolors.ENDC}")
                continue
            
            dl_size = os.stat(f"{dl_dir}/{new_filename}").st_size
            files_downloaded += 1
            bytes_downloaded += dl_size
            

            dl_size = bytesize_to_readable(dl_size)
            print(print_prefix + f"{bcolors.OKGREEN}Downloaded{bcolors.ENDC}  {new_filename}"+f" ({dl_size})" + print_suffix)
            time.sleep(0.01)
            hash_arr.append(hashed_file)
        else:
            print(print_prefix + f"{bcolors.WARNING} Skipped {bcolors.ENDC} {filename}.pdf: Duplicate")
    

    print("================================================")
    print(f"   Downloaded {files_downloaded} files for a total of {bytesize_to_readable(bytes_downloaded, failsafe=False)}.")
    print("================================================\n")



def scraper(subject):
    #starts the scraper
    subject = subject.upper()

    with open("src/subjects.json", "r+") as file:
        subject_dict = json.load(file)
    try:
        dav_url = "https://www-dav.uio.no"+subject_dict[subject]
        path_prefix = subject_dict[subject].replace("/studier/emner/", "")
    except KeyError:
        print(f"Subject '{subject}' not found")
        sys.exit(1)

    # check if .mnt is already mounted, and unmount it if it is.
    if Mounter.mnt_is_mounted():
        Mounter.unmount_webdav()
    Mounter.mount_webdav(dav_url.replace("https://www-dav.uio.no/studier/emner/", "")) 
    atexit.register(Mounter.unmount_webdav) # add failsafe in case process is aborted early
    download_subject(subject, path_prefix)
    atexit.unregister(Mounter.unmount_webdav)
    Mounter.unmount_webdav()


parser = argparse.ArgumentParser(description='Scrape all semester pages of a UiO subject in order to get the urls of PDFs of old exams and their solutions.\n Made by Bror Hjemgaard, 2021')
parser.add_argument('SUBJECT', metavar='SUBJECT', nargs=1,
                    help='Subject code of any UiO subject. Case insensitive')
parser.add_argument("-i", metavar="expr",nargs="*", help="Patterns to ignore in filenames. Pdfs with names containing these will not be downloaded")

parser.add_argument("-s", metavar="sem",nargs="*", help="Which semesters to look for files in, i.e H16, S21 (or V21 for the norwegians). Single digits must be zero-left padded")

if __name__ == '__main__':
    args = parser.parse_args()
    subject = args.SUBJECT[0]
    passed_ignore_patterns = args.i 
    semesters = args.s
    scraper(subject)
    
