import os
import pathlib
import platform
import random
import re
import shutil
import subprocess
import time
from os import path
from subprocess import check_output, DEVNULL

import psutil
import requests
from loguru import logger


def initialize_vpn(server_to_connect_to:str, nordvpn_username=None, nordvpn_password=None, token=None):
    """
    Function used to instantiate the NordVPN app, so we can connect later.
    :param nordvpn_username: this will be used if the user is not logged in his NordVPN account
    :param nordvpn_password: this will be used if the user is not logged in his NordVPN account
    :param token: this will be used if the user is not logged in his NordVPN account
    :param server_to_connect_to: The name of the location to connect to, e.g: france, europe

    """
    server_to_connect_to = server_to_connect_to.strip().lower()
    opsys = platform.system()
    cwd_path = None
    if opsys == "Windows":
        cwd_path = start_vpn_windows()

    elif opsys == "Linux":
        start_vpn_linux(nordvpn_username=nordvpn_username, nordvpn_password=nordvpn_password, token=token)
    else:
        raise Exception("I'm sorry, NordVPN switcher only works for Windows and Linux machines.")

    HERE = pathlib.Path(__file__).parent
    areas_list = [x.lower().strip() for x in open(HERE / "NordVPN_options" / "countrylist.txt", 'r').readlines()]
    country_dict = {'countries': areas_list[0:60], 'europe': areas_list[0:36], 'americas': areas_list[36:44],
                    'africa east india': areas_list[49:60], 'asia pacific': areas_list[49:60],
                    'regions australia': areas_list[60:65], 'regions canada': areas_list[65:68],
                    'regions germany': areas_list[68:70], 'regions india': areas_list[70:72],
                    'regions united states': areas_list[72:87], 'special groups': areas_list[87:len(areas_list)]}

    # set base command according to running os#
    if opsys == "Windows":
        nordvpn_command = ["nordvpn", "-c"]
    else:
        nordvpn_command = ["nordvpn", "c"]

    if opsys == "Windows":
        nordvpn_command.append("-g")

    # If asked for specific region (e.g. europe)#
    if server_to_connect_to in country_dict.keys():
        sample_countries = country_dict[server_to_connect_to]

        # take a random from the list
        server_to_connect_to = random.choice(sample_countries)

    # In linux, we need to replace spaces by underscores
    if server_to_connect_to.count(" ") > 0 and opsys == "Linux":
        server_to_connect_to = re.sub(" ", "_", server_to_connect_to)

    parameters = {
        "platform": opsys,
        "server_to_connect_to": server_to_connect_to,
        "command": nordvpn_command,
        "cwd_path": cwd_path,  # windows specific
    }

    logger.info("Done!")

    return parameters


def start_vpn_linux(nordvpn_username, nordvpn_password, token):
    logger.info("You're using Linux.\n"
                "Performing system check...\n")

    # check if nordvpn is installed on linux#
    if shutil.which("nordvpn"):
        logger.info("NordVPN installation check: OK")
    else:
        raise Exception("NordVPN is not installed on your Linux machine.\n")

    # check if user is logged in. If not, ask for credentials and log in or use credentials from stored settings if available.#
    check_nord_linux_acc = str(check_output(["nordvpn", "account"]))
    if "not logged in" in check_nord_linux_acc:
        try:
            if token:
                login_nordvpn = check_output(["nordvpn", "login", "--token", token])
            else:
                login_nordvpn = check_output(["nordvpn", "login", "-u", nordvpn_username, "-p", nordvpn_password])
        except subprocess.CalledProcessError:
            raise Exception("Sorry,something went wrong while trying to log in")
        if "Welcome" in str(login_nordvpn):
            logger.info("Login successful !")
        else:
            raise Exception("Sorry, NordVPN throws an unexpected message, namely:\n" + str(login_nordvpn))


def start_vpn_windows():
    logger.info("You're using Windows.\n"
                "Performing system check...\n")

    # seek and set windows installation path#
    option_1_path = 'C:/Program Files/NordVPN'
    option_2_path = 'C:/Program Files (x86)/NordVPN'
    if path.exists(option_1_path):
        cwd_path = option_1_path
    elif path.exists(option_2_path):
        cwd_path = option_2_path
    else:
        custom_path = input(
            "It looks like you've installed NordVPN in an uncommon folder. Would you mind telling me which folder? (e.g. D:/customfolder/nordvpn)")
        while not path.exists(custom_path):
            custom_path = input(
                "I'm sorry, but this folder doesn't exist. Please double-check your input.")
        while not os.path.isfile(custom_path + "/NordVPN.exe"):
            custom_path = input(
                "I'm sorry, but the NordVPN application is not located in this folder. Please double-check your input.")
        cwd_path = custom_path
    logger.info("NordVPN installation check: OK")

    # check if nordvpn service is already running in the background
    check_service = "nordvpn-service.exe" in (p.name() for p in psutil.process_iter())
    if check_service is False:
        raise Exception(
            "NordVPN service hasn't been initialized, please start this service in [task manager] --> [services] and restart your script")
    logger.info("NordVPN service check: OK")

    # start NordVPN app and disconnect from VPN service if necessary#
    logger.info("Opening NordVPN app and disconnecting if necessary...")
    open_nord_win = subprocess.Popen(["nordvpn", "-d"], shell=True, cwd=cwd_path, stdout=DEVNULL)
    while not ("NordVPN.exe" in (p.name() for p in psutil.process_iter())):
        logger.info("Waiting for NordVPN.exe to pop in processes.")
        time.sleep(1)

    open_nord_win.kill()
    logger.info("NordVPN app launched: OK")

    return cwd_path


def rotate_VPN(parameters: dict):
    opsys = parameters['platform']
    command = parameters['command']
    server_to_connect_to = parameters["server_to_connect_to"]
    cwd_path = parameters.get('cwd_path')  # windows specifc

    # try to get the current ip to check later if it has changed
    current_ip = check_old_ip()

    if not current_ip:
        raise Exception("Couldn't get the currentIP, check if our API to check ip is still valid.")

    # tries to connect to server
    logger.info(f"Connecting you to {server_to_connect_to}")
    old_ip = current_ip
    connect_to_server(command, cwd_path, opsys, server_to_connect_to)

    check_ip_changed(old_ip)

    logger.info("Done! Enjoy your new server.")


def check_ip_changed(old_ip):
    for _ in range(12):
        try:
            new_ip = get_current_ip()
        except Exception:
            logger.info(f"Error on api.myip server may still be connecting, waiting 5s ...")
            time.sleep(5)
            continue

        if new_ip != old_ip:
            logger.info(f"Perfect ! Now new IP {new_ip} is different from old IP {old_ip}")
            break


def check_old_ip():
    current_ip = None
    for _ in range(3):
        try:
            current_ip = get_current_ip()
        except Exception as e:
            logger.info("Can't fetch current ip. Retrying in 3s...")
            time.sleep(3)
            continue
        logger.info(f"Your current ip-address is: {current_ip}")
        break
    return current_ip


def get_current_ip():
    new_ip = requests.get('https://api.myip.com/').json()['ip']
    return new_ip


def connect_to_server(command, cwd_path, opsys, server_to_connect_to: str):
    try:
        command = command + [server_to_connect_to]
        if opsys == "Windows":
            new_connection = subprocess.run(command, shell=True, cwd=cwd_path)
        else:
            new_connection = check_output(command)
            logger.info("Found a server! You're now on " +
                        re.search('(?<=You are connected to )(.*)(?=\()', str(new_connection))[0].strip())
    except Exception:
        logger.info("An unknown error occurred while connecting to a different server! Retrying...")
        logger.exception("Sleeping for 15s before retry")
        time.sleep(15)


def close_vpn_connection(parameters: dict):
    opsys = parameters['platform']
    cwd_path = parameters.get('cwd_path')  # windows specifc

    logger.info("Disconnecting...")
    if opsys == "Windows":
        terminate = subprocess.Popen(["nordvpn", "-d"], shell=True, cwd=cwd_path, stdout=DEVNULL)
    else:
        terminate = subprocess.Popen(["nordvpn", "d"], stdout=DEVNULL)

    terminate.wait()
    logger.info("Done!")
