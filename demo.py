from nordvpn_switch import initialize_VPN, rotate_VPN, terminate_VPN

destination = "France"

nordvpn_username = ""
nordvpn_password = ""

settings = initialize_VPN(destination, nordvpn_username,  nordvpn_password)
rotate_VPN(settings)




terminate_VPN(settings)
