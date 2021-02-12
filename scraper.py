import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


def get_hash_from_file(path):
    # returns a unique utf-8 encoded hash of pdf at given path
    m = hashlib.md5()
    try:
        with open(path, "rb") as file:
            m.update( file.read())
    except:
        # if the above fails, create a hash from just the filename
        print("hash fail")
        m.update(path)
    return m.digest()


def generate_hash_file(dir, store=True):
    # generate a hash file from the pdfs within the given dir 
    globber = [str(file) for file in Path(dir).rglob('*.pdf')]#glob.glob(dir+"/*.pdf")
    hash_arr = np.array(["a"*16]*len(globber), dtype=bytes)
    for i,path in enumerate(globber):
        hash_arr[i] = get_hash_from_file(path)
    if store:
        np.save(dir+"/.hashes", hash_arr, allow_pickle=True, fix_imports=True)
    return hash_arr



def download_subject(subject):
    # starts the downloading process. Also makes sure that no duplicate files are downloaded

    dl_dir = os.path.abspath("./downloads/"+subject) # dir to be downloaded into
    if not os.path.isdir(dl_dir): # if not dir exists, create it 
        subprocess.run(["mkdir", "-p", dl_dir])

    hash_arr = list(generate_hash_file(dl_dir, store=False)) # create an empty hash file and get an empty list of correct length
    
    for file in Path('./mnt/').rglob('*.pdf'):
        
        hashed_file = get_hash_from_file(file)
        if hashed_file not in hash_arr:
            # if this succeeds, then the pdf is unique and will be downloaded
            subprocess.run(["cp", file, dl_dir +"/."])
            print(f"Downloaded {file}")
            time.sleep(0.1)
            hash_arr.append(hashed_file)
        else:
            pass
            print(f"file {file} not unique! Skipping!")
    generate_hash_file(dl_dir)
   
def mount_webdav(url):
    # mounts the url into the mnt/ dir
    subprocess.run(["mkdir", "-p", "mnt"])
    print("Please enter UiO username and password")
    subprocess.run(["wdfs", url, "mnt"])
    print("succesfully mounted into ./mnt")
    
    
    
def unmount_webdav():
    # unmounts the mnt/ dir
    time.sleep(0.5)
    subprocess.run((["mount", "-a"]))
    time.sleep(0.5) # some sleeping, as it makes the unmouning more reliant
    subprocess.run(["fusermount", "-u", "mnt/"])
    print("Unmounting process finished")



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

    mount_webdav(dav_url) 
    try:
        download_subject(subject)
        unmount_webdav()
    except:
        unmount_webdav()
        raise Exception


try:
    scraper(sys.argv[1])
except KeyboardInterrupt:
    unmount_webdav()
