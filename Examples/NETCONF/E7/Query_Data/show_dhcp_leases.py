# IMPORT STATEMENT
from CMSNBIClient import CMS_NBI_Client, Query_E7_Data

# IMPORT STATEMENT

# Create the CMS_NBI_Client() instance
client = CMS_NBI_Client()

# Next step is to submit a login request to the CMS server, I will be using an example node
client.login_netconf(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    cms_user_pass=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["pass_wd"],
    cms_node_ip=client.cms_nbi_config["cms_nodes"]["example_node"]["connection"]["cms_node_ip"],
    uri=client.cms_nbi_config["cms_netconf_uri"]["e7"],
)
# if the login_netconf() function is successful a tuple with (True, '') is returned  else a response.response object is returned
# you can use the response library to debug the response.response object

# Next we create a Query_E7_Data instance and pass the CMS_NBI_Client instance to it
query_e7_data = Query_E7_Data(client)

# Once the Query_E7_Data() instance has been created, we can now begin using the built-in show_dhcp_leases() functions
# This query will submit query to the CMS node requesting dhcp information for the specified network_name(ie E7 node)

# submitting show_dhcp_leases() with no action_args, is the same as show-dhcp-leases in the CLI
# -----------------IMPORTANT NOTE-------------------------------
# During my testing a http_timeout of 5 seemed to work, your mileage may very depend on response time from the server
# Each http(s) request will be answered with a max number of 5 dhcp-lease entries.
#   this means that for 20 dhcp-leases stored on an E7 node it will take 4 http(s) queries to retrieve the 20 dhcp-lease entry's
query_e7_data.show_dhcp_leases(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=5,
)

# Similar to the other query functions we can also pass filters to the action_arg parameter
# ---------LIST OF FILTERS----------
# vlan:"1"
# ontethge:{'ont':'1','ontethge':'1'}
# ontethfe:{'ont': '1', 'ontethfe': '1'}
# ethintf:{'ethintf': {'shelf': '1','card': '1', 'ethintf': '103'}}
# gponport:{'shelf': '1', 'card': '1', 'gponport': '1'}

# QUERY ON A SPECIFIED VLAN
query_e7_data.show_dhcp_leases(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=5,
    action_args={"vlan": "1"},
)

# QUERY ON A SPECIFIED GE(GIG-ETHERNET) ON AN ONT
# you will need to pass the ont-id and the ontethge-id
query_e7_data.show_dhcp_leases(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=5,
    action_args={"ontethge": {"ont": "1", "ontethge": "1"}},
)

# QUERY ON A SPECIFIED FE(FAST-ETHERNET) ON AN ONT
# you will need to pass the ont-id and the ontethfe-id
query_e7_data.show_dhcp_leases(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=5,
    action_args={"ontethfe": {"ont": "1", "ontethfe": "1"}},
)

# QUERY ON A SPECIFIC GPONPORT
# you will need to pass the shelve-id, card-id, and gponport-id
# This example would be for gponport with an id of 1/1/1
query_e7_data.show_dhcp_leases(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=5,
    action_args={"gponport": {"shelf": "1", "card": "1", "gponport": "1"}},
)

# QUERY ON A SPECIFIC EthIntf
# you will need to pass the shelve-id, card-id, and EthIntf-id
# This example would be for EthIntf with an id of 1/1/103
query_e7_data.show_dhcp_leases(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=5,
    action_args={"ethintf": {"shelf": "1", "card": "1", "ethintf": "103"}},
)
