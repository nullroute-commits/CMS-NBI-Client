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
# if the login_netconf() function is successful a tuple with (True, '') is returned  else a requests.models.Response object is returned
# you can use the response library to debug the requests.models.Response object

# Next we create a Query_E7_Data instance and pass the CMS_NBI_Client instance to it
query_e7_data = Query_E7_Data(client)

# Once the query instance is created we can then call the system_children_vlan() function to pull all vlans from the e7
# ------IMPORTANT NOTE-------
# THE CMS NODE WILL ONLY RESPOND WITH 3 VLAN ENTRIES PER HTTP(S) Request, so keep that in mind

query_e7_data.system_children_vlan(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
)

# GUESS WHAT WE CAN SUBMIT FILTERS TO THE system_children_vlan() function and have the CMS node do all the filtering.

# ----LIST OF FILTERS AND FORMATS------
# |-------KEY--------|--------VALUE--------|
# 'ae-ont-discovery': 'false' or 'true'
#  'dhcp-mode': 'none' or 'snoop' or 'proxy,
#  'igmp-mode': 'snoop-suppress' or 'proxy' or 'flood',
#  'igmp-pbit': 'pbit-4',
#  'igmp-prof': {'igmp-prof': {'type': 'VlanIgmpProf', 'id': {'vlanigmpprof': '1'}}},
#  'eth-opt82prof': {'type': 'Opt82Prof', 'id': {'opt82prof': '1'}}
#  'gpon-opt82prof': {'type': 'Opt82Prof', 'id': {'opt82prof': '1'}}
#  'pppoe-prof': {'type': 'PppoeProf', 'id': {'pppoeprof': '1'}}
#  'ip-src-verify': 'true' or 'false',
#  'mac-force-forw': 'true' or 'false',
#  'mac-learn': 'true' or 'false',
#  'mobility': 'true' or 'false',
#  'name': 'Example Vlan',
#  'option82-enable': 'true' or 'false',
#  'pon-hairpin': 'true' or 'false',
#  'pon-tlan': 'true' or 'false',

# QUERYING A VLAN BY NAME
query_e7_data.system_children_vlan(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    attr_filter={"name": "Example Vlan"},
)

# QUERYING FOR ALL VLAN WITH DHCP-SNOOPING ENABLED
query_e7_data.system_children_vlan(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    attr_filter={"dhcp-mode": "snoop"},
)

# QUERY FOR ALL VLAN WITH DHCP-SNOOP ENABLED AND IGMP-MODE FLOOD
query_e7_data.system_children_vlan(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    attr_filter={"dhcp-mode": "snoop", "igmp-mode": "flood"},
)

# QUERY FOR ALL VLAN WITH A PPPOE PROFILE ID of 1 APPLIED
query_e7_data.system_children_vlan(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    attr_filter={"pppoe-prof": {"type": "PppoeProf", "id": {"pppoeprof": "1"}}},
)

# QUERY FOR ALL VLANS WITH THE TVLAN ATTRIBUTE
query_e7_data.system_children_vlan(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    attr_filter={"pon-tlan": "true"},
)


# When you need to query a specific vlan, we can use the vlan() function
# all you need to do is pass it the id
query_e7_data.vlan(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    vlan_id="1",
)
