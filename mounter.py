import os
import subprocess
import time
import re
import sys

class mountcolors:
    OKGREEN = '\033[92m'
    ALERT = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m' 

class Mounter:
    session_code = "UiOScrapeWDFS"

    def mount_webdav(url):
        """
        Mounts the webdav fs into .mnt
        """
        subprocess.run(["mkdir", "-p", ".mnt"]) # create the .mnt dir if it does not already exist
        
        
        # THIS SECTION IS WHERE THE PROGRAM PROMPTS FOR USERNAME AND PASSWORD. 
        # Below is the wdfs call which mounts the subject folders and handles all credentials.
        mount_args = f"wdfs {url} .mnt -o ro -o auto_unmount -o sync_read -o intr -o accept_sslcert -o noforget -o fsname={Mounter.session_code}"
        print("Please enter UiO username and password. (Check readme if you wonder why you have to enter your username and password)")
        for i in range(3): # give three attempts
            res = subprocess.Popen(mount_args, shell=True, stderr=subprocess.PIPE)
            res.wait()
            if res.returncode == 0: # wdfs process confirms credentials
                break
            else: # wdfs returns an error code (most likely due to wrong credentials). All errors are funneled into the case of wrong credentials
                print(f"[{i+1}/3] Wrong username/password")
            if i == 2:
                print(f"Too many wronge attempts. Try again or contact developer if this problem keeps occuring")
                sys.exit()

        # simple check to confirm that the mounting was successful
        
        while not Mounter.mnt_is_mounted():
            time.sleep(0.1)
        print("Mounting successful")
        
 

    def unmount_webdav():
        """
        Performs a safe unmounting of the mounted davfs. 
        There is one main solution, and one backup. 
        Primarily, the unmounting process is done by stopping the main wdfs process which automatically unmounts the fs. 
        If this fails, the unmounting is performed by repeatedly calling fusermount. 
            This works but is less elegant nad often takes longer time as it requires the wdfs process to finish, which can take a long time. This is often a last resort"""

        pid_locator_re = re.compile(r"^\s*?(\d+)(?:.+?)fsname="+Mounter.session_code+r"(?:.+?).+\n\s*(\d+)(?:.+?)wdfs\n")
        proc = subprocess.Popen(["ps", "ax"], stdout=subprocess.PIPE)
        output = subprocess.check_output(('grep', 'wdfs'),stdin=proc.stdout)
        pids = pid_locator_re.findall(output.decode("utf-8"))

        if pids: # if method succesfully located the pid
            pid_local = int(pids[0][0]) # local process. Will end as soon as python script ends
            pid_wdfs = int(pids[0][1]) # wdfs mounting process pid. Must be ended manually in order to ensure swift unmounting
            if abs(pid_local-pid_wdfs) <= 10: # this is a soft test to assert that we are most likely not interferring with any other wdfs processes that the user has initiated, as the pids are relatively close
                killproc = subprocess.Popen(["kill", str(pid_wdfs)])
                killproc.wait()
                return
        
        # if the above fails, the below is alternate unmounting process
        print(f"{mountcolors.ALERT}{mountcolors.BOLD}Traditional unmouting failed. Please wait for this process to finish! Program will exit when done!{mountcolors.ENDC}")

        tries = 0
        while Mounter.mnt_is_mounted() and tries < 100:
    
            unmount_proc = subprocess.Popen(["fusermount", "-u", ".mnt/"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            out, err = unmount_proc.communicate()
            if err:
                tries += 1
            else:
                print(f"{mountcolors.OKGREEN}{mountcolors.BOLD}Done!{mountcolors.ENDC}")
                return

        print("Attempted", tries, "unmounts unsuccessfully. Please manually unmount .mnt/")

    

    mnt_global_path = os.path.abspath(".mnt").__str__() +" "
    mnt_out = lambda: subprocess.Popen(["mount"], stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
    def mnt_is_mounted(): 
        return Mounter.mnt_global_path in Mounter.mnt_out()
            
