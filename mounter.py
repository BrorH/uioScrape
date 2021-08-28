import os
import subprocess
import time
import sys



class Mounter:

    def mount_webdav(url):
        """
        Mounts the webdav fs into .mnt
        """
        subprocess.run(["mkdir", "-p", ".mnt"]) # create the .mnt dir if it does not already exist
        
        # THIS SECTION IS WHERE THE PROGRAM PROMPTS FOR USERNAME AND PASSWORD. 
        
        mount_args = f"mount .mnt"# && bindfs -n .mntParent/{url} .mnt"
        print("Please enter UiO username and password. (Check readme if you wonder why you have to enter your username and password)")
        for i in range(3): # give three attempts
            res = subprocess.Popen(mount_args, shell=True, stderr=subprocess.PIPE)
            res.wait()
            if res.returncode == 0: # process confirms credentials
                break
            else: 
                print(f"[{i+1}/3] Wrong username/password")
            if i == 2:
                print(f"Too many wrong attempts. Try again or contact developer if problem persists")
                sys.exit()

        
        # simple check to confirm that the mounting was successful
        while not Mounter.mnt_is_mounted():# and not Mounter.mntParent_is_mounted():
            time.sleep(0.1)
        print("Mounting successful")
 
    def unmount_webdav():
        """
        Performs a safe unmounting of the two mounted webdav filesystems in .mnt
        """

        tries = 0
        while Mounter.mnt_is_mounted() and tries < 100:
            
            unmount_proc = subprocess.Popen(["fusermount", "-uz", ".mnt/"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            out, err = unmount_proc.communicate()
            tries += 1
            if not err:
                print("Successfully unmounted .mnt")
                return
            if tries == 100:
                print(err)
                print("Could not unmount .mnt! Please unmount manually. A reboot will also unmount. If problem persists, contact developer")


    
    mnt_global_path = os.path.abspath(".mnt").__str__() +" "
    mnt_out = lambda: subprocess.Popen(["mount"], stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
    def mnt_is_mounted(): 
        return Mounter.mnt_global_path in Mounter.mnt_out()

