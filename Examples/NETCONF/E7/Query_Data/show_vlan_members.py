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

# # Once the query instance is created we can then call the show_vlan_members() function to pull all members of a specific vlan from the e7
query_e7_data.show_vlan_members(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    http_timeout=1,
    vlan_id="10",
)
