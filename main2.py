import glob
import hashlib
import os
import subprocess

import numpy as np


def get_hash_from_file(path):
    # returns a unique utf-8 encoded hash of pdf at given path
    m = hashlib.md5()
    try:
        with open(path, "rb") as file:
            m.update( file.read())
    except:
        # if the above fails, create a hash from just the filename
        m.update(path)
    return m.digest()


def generate_hash_file(dir, store=True):
    # generate a hash file from the pdfs within the given dir 
    globber = glob.glob(dir+"/*.pdf")
    hash_arr = np.array(["a"*16]*len(globber), dtype=bytes)
    for i,path in enumerate(globber):
        hash_arr[i] = get_hash_from_file(path)
    if store:
        np.save(dir+"/.hashes", hash_arr, allow_pickle=True, fix_imports=True)
    return hash_arr



def download_from_dir(dir, subject):
    # starts the downloading process. Also makes sure that no duplicate files are downloaded

    dl_dir = os.path.abspath("downloads/"+subject) # dir to be downloaded into
    if not os.path.isdir(dl_dir): # if not dir exists, create it 
        subprocess.run(["mkdir", "-p", dl_dir])

    hash_arr = list(generate_hash_file(dl_dir, store=False)) # dont need to save, as a new, updated version is soon to be created
   
    for i,file in enumerate(glob.glob(dir+"/*.pdf")):
        hashed_file = get_hash_from_file(file)
        if hashed_file not in hash_arr:
            # if this succeeds, then the pdf is unique and will be downloaded
            subprocess.run(["cp", file, dl_dir +"/."])
            hash_arr.append(hashed_file)
            print(f"Downloaded {file}")
        else:
            pass
            print(f"file {file} not unique! Skipping!")
    generate_hash_file(dl_dir)
   

def mount_dav():



dir = os.path.abspath("./downloads/FYS3120/")
hash_path = os.path.abspath("./downloads/FYS3120/.hashes.npy")
#generate_hash_file(dir)

dl_from_dir = os.path.abspath("./downloads/dl_FYS3120/")
download_from_dir(dl_from_dir, "FYS3120")
# res = np.load(dir+".hashes.npy", allow_pickle=True)
# for id, file in zip(res, glob.glob(dir+"*.pdf")):
#     print(id, file.lstrip(dir))




# if __name__ == '__main__':
#     args = parser.parse_args()
#     max_requests = int(args.requests)
#     speed =float(args.speed)
#     quality = bool(args.Q)
#     download = bool(args.d)
#     subject = args.SUBJECT[0]
#     subjects_dict = eval(np.load(os.path.relpath("./src/subjects.npy"), allow_pickle=True).__repr__().lstrip("array(").rstrip(",\n      dtype=object)\n"))
#     try:
#         print(subjects_dict["UV9920V4"])
#         dav = "https://www-dav.uio.no/studier/emner"+subjects_dict[subject.upper()]
#         print(dav)
#     except KeyError:
#         print(f"Subject '{subject}' not found. Please check your spelling or give up")
#         sys.exit(1)
#     try:
#         subprocess.run(["sudo","./scraper.sh", dav, subject.upper()])
#         listOfFiles = list()
#         for (dirpath, dirnames, filenames) in os.walk("/mnt/dav"):
#             for file in filenames:
#                 if ".pdf" in file and file not in listOfFiles:
#                     listOfFiles += [os.path.join(dirpath, file)]
        
#     except KeyboardInterrupt:
#         listOfFiles = list()
#         for (dirpath, dirnames, filenames) in os.walk("/mnt/dav"):
#             for file in filenames:
#                 if ".pdf" in file and file not in listOfFiles:
#                     listOfFiles += [os.path.join(dirpath, file)]
#         subprocess.run(["sudo","umount", "/mnt/dav"])
#     pdfs = []
#     for file in listOfFiles:
#         if True in [file.lower() in comp for comp in ["lect", "grad", "formula", "formel"]]: continue
#         if file not in pdfs: pdfs.append(file)
#     subprocess.run(["mkdir", "-p","./downloads/"+subject.upper()])
#     subprocess.run(["sudo","chmod","-R","a+rwX","./downloads/"+subject.upper()])
#     for file in pdfs:
#         subprocess.run(["cp", file, "./downloads/"+subject.upper()+"/"+"-".join(file.split("/")[3:])])
#     print("\n".join(pdfs))

