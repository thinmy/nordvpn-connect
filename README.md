# NordVPN-connect

This repo has been forked from https://github.com/kboghe/NordVPN-switcher by Kristof Boghe.  
Thank you for your work.   

## Description
This lib allows you to connect to a NordVPN server. Works on Windows and Linux. 

## Install 

``pip install nordvpn-connect``


## Simple Usage

````python
from nordvpn_connect import initialize_vpn, rotate_VPN, close_vpn_connection

# optional, use this on Linux and if you are not logged in when using nordvpn command

settings = initialize_vpn("France")  # starts nordvpn and stuff
rotate_VPN(settings)  # actually connect to server

# YOUR STUFF

close_vpn_connection(settings)

````

## Usage with credentials (Only Linux)

If when you use `nordvpn` command it asks you for credentials, you'll need to provide them to the `initialize_vpn` function.

````python
from nordvpn_connect import initialize_vpn, rotate_VPN, close_vpn_connection

# optional, use this on Linux and if you are not logged in when using nordvpn command

settings = initialize_vpn("France", "USERNAME", "PASSWORD")  # starts nordvpn and stuff
rotate_VPN(settings)  # actually connect to server

# YOUR STUFF

close_vpn_connection(settings)

````

