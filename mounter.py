import os
import subprocess
import time
import sys



class Mounter:
    session_code = "UiOScrapeWDFS"

    def mount_webdav(url):
        """
        Mounts the webdav fs into .mnt
        """
        subprocess.run(["mkdir", "-p", ".mnt"]) # create the .mnt dir if it does not already exist
        subprocess.run(["mkdir", "-p", ".mntParent"]) # create the .mnt dir if it does not already exist
        
        # THIS SECTION IS WHERE THE PROGRAM PROMPTS FOR USERNAME AND PASSWORD. 
        # Below is the wdfs call which mounts the subject folders and handles all credentials.
        
        mount_args = f"mount .mntParent && bindfs -n .mntParent/{url} .mnt"
        #mount_args = f"wdfs {url} .mnt -o ro -o auto_unmount -o sync_read -o intr -o accept_sslcert -o noforget -o fsname={Mounter.session_code}"
        print("Please enter UiO username and password. (Check readme if you wonder why you have to enter your username and password)")
        for i in range(3): # give three attempts
            res = subprocess.Popen(mount_args, shell=True, stderr=subprocess.PIPE)
            res.wait()
            if res.returncode == 0: # wdfs process confirms credentials
                break
            else: # wdfs returns an error code (most likely due to wrong credentials). All errors are funneled into the case of wrong credentials
                print(f"[{i+1}/3] Wrong username/password")
            if i == 2:
                print(f"Too many wrong attempts. Try again or contact developer if problem persists")
                sys.exit()

        
        # simple check to confirm that the mounting was successful
        while not Mounter.mnt_is_mounted() and not Mounter.mntParent_is_mounted():
            time.sleep(0.1)
        print("Mounting successful")
        
 

    def unmount_webdav():
        """
        Performs a safe unmounting of the two mounted webdav filesystems in .mnt and .mntParent. 
        """

        tries = 0
        while Mounter.mnt_is_mounted() and tries < 100:
            
            unmount_proc = subprocess.Popen(["fusermount", "-uz", ".mnt/"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            out, err = unmount_proc.communicate()
            tries += 1
            if not err:
                print("Successfully unmounted .mnt")
                break
            if tries == 100:
                print(err)
                print("Could not unmount .mnt! Please unmount manually. A reboot will also unmount. If problem persists, contact developer")

        tries = 0
        while Mounter.mntParent_is_mounted() and tries < 100:
            unmount_proc = subprocess.Popen(["fusermount", "-uz", ".mntParent/"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            out, err = unmount_proc.communicate()
            tries += 1
            if not err:
                print("Successfully unmounted .mntParent")
                return
            if tries == 100:
                print(err)
                print("Could not unmount .mntParent! Please unmount manually. A reboot will also unmount. If problem persists, contact developer")


    
    mnt_global_path = os.path.abspath(".mnt").__str__() +" "
    mnt_out = lambda: subprocess.Popen(["mount"], stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
    def mnt_is_mounted(): 
        return Mounter.mnt_global_path in Mounter.mnt_out()

    mntParent_global_path = os.path.abspath(".mntParent").__str__() +" "
    mntParent_out = lambda: subprocess.Popen(["mount"], stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
    def mntParent_is_mounted(): 
        return Mounter.mntParent_global_path in Mounter.mntParent_out()  
            
