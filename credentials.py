import secrets
import subprocess
import sys
from base64 import urlsafe_b64decode as b64d
from base64 import urlsafe_b64encode as b64e
from getpass import getpass

import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

backend = default_backend()
iterations = 100_000

def _derive_key(password: bytes, salt: bytes, iterations: int = iterations) -> bytes:
    """Derive a secret key from a given password and salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        iterations=iterations, backend=backend)
    return b64e(kdf.derive(password))


def password_decrypt(token: bytes, password: str) -> bytes:
    decoded = b64d(token)
    salt, iter, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter, 'big')
    key = _derive_key(password.encode(), salt, iterations)
    return Fernet(key).decrypt(token)

def password_encrypt(message: bytes, password: str, iterations: int = iterations) -> bytes:
    salt = secrets.token_bytes(16)
    key = _derive_key(password.encode(), salt, iterations)
    return b64e(
        b'%b%b%b' % (
            salt,
            iterations.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message)),
        )
    )

def dav_login(url):
    with open(".credentials", "r+") as file: 
        uname, p_token = tuple(file.readlines())
    for i in range(3):
        pin = getpass("Enter pin >>")
        try:
            return ["-o", "username="+uname, "-o", "password="+password_decrypt(p_token.encode("utf-8"), pin).decode()]
        except cryptography.fernet.InvalidToken:
            
            print(f"Wrong pin [{i+1}/3]")
            if i == 2: 
                print("Wrong pin entered 3 times. If you forgot your pin, re-run credentials.py")
                print("Terminating ...")
                sys.exit(1)

def prompt_creds():
    print("Enter a pin of choice to be used to acces UiOScrape. Must be 4 or more unicode chars")
    pin_ = getpass(">>")
    if len(pin_) < 4: 
        print("Too short! Must be at least 4 characters")
        return prompt_creds()
    print("Enter again to confirm")
    pin = getpass(">>")
    if pin != pin_:
        print("ERROR! Pins dont match.")
        prompt_creds()
    return pin


if __name__ == "__main__":
    print(f"This script lets you generate an encrypted pin for UiOScrape, instead of having to provide your full username and password each time.\nThe encrypted file is stored locally. \nA pin is not reccomended if you are not the only user of this computer.")
    print(f"UiOScrape is open source, meaning you can check for yourself that nothing suspicious is happening to your stored credentials.\nThis solution is meant for those who intend to frequenctly use UiOScrape whilst not want to be interrupted by credential prompts.\n")
    print("Enter UiO Username:")
    uname = input(">>")
    print("Enter UiO Password:")
    p = getpass(">>")
    pin = prompt_creds()


    token = password_encrypt(p.encode(), pin)
    with open("./.credentials", "w+") as file:
        file.write(uname +"\n")
        file.write(token.decode("utf-8"))
    print("Done! You may now attempt to use UiOScrape with your pin!")
 