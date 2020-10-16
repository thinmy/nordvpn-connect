from nordvpn_connect import initialize_vpn, rotate_VPN, close_vpn_connection

destination = "France"

nordvpn_username = ""
nordvpn_password = ""

settings = initialize_vpn(destination, nordvpn_username, nordvpn_password)
rotate_VPN(settings)




close_vpn_connection(settings)
