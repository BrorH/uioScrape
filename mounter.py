import os
import subprocess
import time

from credentials import dav_login

mnt_global_path = os.path.abspath(".mnt").__str__() +" "
mnt_out = lambda: subprocess.Popen(["mount"], stdout=subprocess.PIPE).communicate()[0].decode("utf-8")

def mount_webdav(url):
    # mounts the url into the .mnt/ dir
    mount_args = ["wdfs", url, ".mnt", "-o", "ro", "-o", "auto_unmount"]
    if os.path.isfile(".credentials"):
        mount_args += dav_login(url)
    else:
        print("Please enter UiO username and password. (Run credentials.py in order to set up a pin to avoid having to enter username/password every time)")
    subprocess.run(["mkdir", "-p", ".mnt"])
    subprocess.run(mount_args)
    print("Mounting...")
    while mnt_global_path not in mnt_out():
        time.sleep(0.5)
    print("Mounting successful")
    
class mountcolors:
    OKGREEN = '\033[92m'
    ALERT = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'  

def unmount_webdav():
    # performs a safe unmount
    
    print(f"{mountcolors.ALERT}{mountcolors.BOLD}Unmounting. Please wait for process to finish! Program will exit when done!{mountcolors.ENDC}")
    FNULL = open(os.devnull, 'w')
    subprocess.run(["mount", "-a"])
    time.sleep(0.1)
    subprocess.run(["bash", "unmounter.sh", mnt_global_path])

    # below is a failsafe in case the bash script fails
    tries = 0
    while mnt_global_path in mnt_out():
        
        tries += 1
        subprocess.run(["fusermount", "-u", ".mnt/"], stdout=FNULL, stderr=FNULL)

        if tries >= 100:
            print("Attempted", tries, "unmounts unsuccessfully. Please manually unmount .mnt/")
            return 
        if tries > 1:
            subprocess.run(["mount", "-a"])
            time.sleep(0.5)
    subprocess.run(["rmdir", ".mnt"])
    print(f"{mountcolors.OKGREEN}{mountcolors.BOLD}Done!{mountcolors.ENDC}")

def init_mountcheck():
    # called at scraper initialization to ensure that nothing is already mounted
    if not os.path.isdir(".mnt"): return

    if len(os.listdir('.mnt') ) == 0: 
        subprocess.run(["rmdir", ".mnt"])
        return

    # if the function call gets this far, then cleanup is needed
    unmount_webdav()
    subprocess.run(["rmdir", ".mnt"])
    


