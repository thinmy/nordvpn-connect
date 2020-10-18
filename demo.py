from nordvpn_connect import initialize_vpn, rotate_VPN, close_vpn_connection

destination = "italy"

nordvpn_username = ""
nordvpn_password = ""

settings = initialize_vpn(destination)
rotate_VPN(settings)

# YOUR STUFF

close_vpn_connection(settings)
