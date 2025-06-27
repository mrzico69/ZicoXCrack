import os
import hashlib
import subprocess
import json
from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)
CONFIG_FILE = os.path.expanduser("~/.zico_config.json")

def show_banner():
    banner = r"""
                                                                                                                              
                                                       ,--.                     ,----,                       ,----..           
  ,----..  ,-.----.      ,---,         ,----..     ,--/  /|                   .'   .`|   ,---,  ,----..     /   /   \          
 /   /   \ \    /  \    '  .' \       /   /   \ ,---,': / '                .'   .'   ;,`--.' | /   /   \   /   .     :         
|   :     :;   :    \  /  ;    '.    |   :     ::   : '/ /               ,---, '    .'|   :  :|   :     : .   /   ;.  \        
.   |  ;. /|   | .\ : :  :       \   .   |  ;. /|   '   ,   ,--,  ,--,   |   :     ./ :   |  '.   |  ;. /.   ;   /  ` ;        
.   ; /--` .   : |: | :  |   /\   \  .   ; /--` '   |  /    |'. \/ .`|   ;   | .'  /  |   :  |.   ; /--` ;   |  ; \ ; |        
;   | ;    |   |  \ : |  :  ' ;.   : ;   | ;    |   ;  ;    '  \/  / ;   `---' /  ;   '   '  ;;   | ;    |   :  | ; | '        
|   : |    |   : .  / |  |  ;/  \   \|   : |    :   '   \    \  \.' /      /  ;  /    |   |  ||   : |    .   |  ' ' ' :        
.   | '___ ;   | |  \ '  :  | \  \ ,'.   | '___ |   |    '    \  ;  ;     ;  /  /--,  '   :  ;.   | '___ '   ;  \; /  |        
'   ; : .'||   | ;\  \|  |  '  '--'  '   ; : .'|'   : |.  \  / \  \  \   /  /  / .`|  |   |  ''   ; : .'| \   \  ',  /         
'   | '/  ::   ' | \.'|  :  :        '   | '/  :|   | '_\.'./__;   ;  \./__;       :  '   :  |'   | '/  :  ;   :    /          
|   :    / :   : :-'  |  | ,'        |   :    / '   : |    |   :/\  \ ;|   :     .'   ;   |.' |   :    /    \   \ .'           
 \   \ .'  |   |.'    `--''           \   \ .'  ;   |,'    `---'  `--` ;   |  .'      '---'    \   \ .'      `---`             
  `---`    `---'                       `---`    '---'                  `---'                    `---`                          
    """
    print(Fore.CYAN + banner)
    print(Fore.LIGHTBLUE_EX + " " * 50 + "🔐 ZICO - Hash Cracking Toolkit 🔐\n" + Style.RESET_ALL)

def identify_hash(hash_str):
    length = len(hash_str)
    if length == 32:
        return "MD5"
    elif length == 40:
        return "SHA1"
    elif length == 64:
        return "SHA256"
    else:
        return "Unknown"

def crack_with_wordlist(hash_str, hash_type, wordlist_path):
    if not os.path.isfile(wordlist_path):
        print(Fore.RED + "[!] Wordlist file not found.")
        return
    print(Fore.YELLOW + f"[+] Cracking {hash_type} hash using Python wordlist attack...")
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in tqdm(f, desc="Wordlist cracking", ncols=75):
                word = line.strip()
                if hash_type == "MD5":
                    hashed = hashlib.md5(word.encode()).hexdigest()
                elif hash_type == "SHA1":
                    hashed = hashlib.sha1(word.encode()).hexdigest()
                elif hash_type == "SHA256":
                    hashed = hashlib.sha256(word.encode()).hexdigest()
                else:
                    print(Fore.RED + "[!] Unsupported hash type for wordlist cracking.")
                    return
                if hashed == hash_str:
                    print(Fore.GREEN + f"[✔] Password found: {word}")
                    return
        print(Fore.RED + "[✘] Password NOT found in wordlist.")
    except Exception as e:
        print(Fore.RED + f"[!] Error during cracking: {e}")

def use_hashcat(hash_str, hash_type, wordlist_path):
    modes = {"MD5": "0", "SHA1": "100", "SHA256": "1400"}
    if hash_type not in modes:
        print(Fore.RED + "[!] Hash type not supported by Hashcat.")
        return
    if not os.path.isfile(wordlist_path):
        print(Fore.RED + "[!] Wordlist file not found.")
        return
    cmd = f"hashcat -m {modes[hash_type]} -a 0 '{hash_str}' '{wordlist_path}' --force"
    print(Fore.YELLOW + f"[>] Running: {cmd}\n")
    subprocess.call(cmd, shell=True)

def use_john(hash_str, hash_type, wordlist_path):
    format_map = {"MD5": "raw-md5", "SHA1": "raw-sha1", "SHA256": "raw-sha256"}
    if hash_type not in format_map:
        print(Fore.RED + "[!] Hash type not supported by John the Ripper.")
        return
    if not os.path.isfile(wordlist_path):
        print(Fore.RED + "[!] Wordlist file not found.")
        return
    tmp_file = "temp_hash.txt"
    with open(tmp_file, "w") as f:
        f.write(hash_str + "\n")
    cmd = f"john --format={format_map[hash_type]} --wordlist='{wordlist_path}' {tmp_file}"
    print(Fore.YELLOW + f"[>] Running: {cmd}\n")
    subprocess.call(cmd, shell=True)
    os.remove(tmp_file)

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except Exception as e:
        print(Fore.RED + f"[!] Failed to save config: {e}")

def load_config():
    if not os.path.isfile(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def main():
    show_banner()
    config = load_config()
    wordlist_path = config.get("wordlist_path", "")

    if not wordlist_path or not os.path.isfile(wordlist_path):
        print(Fore.YELLOW + "No wordlist path saved or file not found.")
        wordlist_path = input("Enter full path to your wordlist file: ").strip()
        if not os.path.isfile(wordlist_path):
            print(Fore.RED + "Invalid file path. Exiting.")
            return
        config["wordlist_path"] = wordlist_path
        save_config(config)
        print(Fore.GREEN + "Wordlist path saved!")

    while True:
        user_hash = input(Fore.CYAN + "\nEnter your hash (or 'exit' to quit): ").strip()
        if user_hash.lower() == "exit":
            print(Fore.LIGHTMAGENTA_EX + "Goodbye! 🔥")
            break

        hash_type = identify_hash(user_hash)
        print(Fore.LIGHTGREEN_EX + f"Detected hash type: {hash_type}")

        print(Fore.LIGHTBLUE_EX + """
Choose an option:
1) Crack with Python wordlist attack
2) Crack with Hashcat (uses saved wordlist)
3) Crack with John the Ripper (uses saved wordlist)
4) Change wordlist path
5) Exit
""")

        choice = input(Fore.YELLOW + "Enter choice: ").strip()
        if choice == "1":
            crack_with_wordlist(user_hash, hash_type, wordlist_path)
        elif choice == "2":
            use_hashcat(user_hash, hash_type, wordlist_path)
        elif choice == "3":
            use_john(user_hash, hash_type, wordlist_path)
        elif choice == "4":
            new_path = input("Enter new full path to wordlist file: ").strip()
            if os.path.isfile(new_path):
                wordlist_path = new_path
                config["wordlist_path"] = wordlist_path
                save_config(config)
                print(Fore.GREEN + "Wordlist path updated!")
            else:
                print(Fore.RED + "Invalid file path.")
        elif choice == "5":
            print(Fore.LIGHTMAGENTA_EX + "Goodbye! 🔥")
            break
        else:
            print(Fore.RED + "Invalid choice, try again.")

if __name__ == "__main__":
    main()
