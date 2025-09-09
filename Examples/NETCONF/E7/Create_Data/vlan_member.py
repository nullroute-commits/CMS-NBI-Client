# IMPORT STATEMENT
from CMSNBIClient import CMS_NBI_Client, Create_E7_Data

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
# if the login_netconf() function is successful a tuple with (True, '') is returned  else a response.Models.Response object is returned
# you can use the response library to debug the response.models.response object

# Next we create a Create_E7_Data instance and pass the CMS_NBI_Client instance to it
create_e7_data = Create_E7_Data(client)

# Once the Create_E7_Data object is created we can then call the vlan_members() function and add an interface to the vlan membership
# ------IMPORTANT NOTE------
# You will need to submit the correct structured dictionary to the int_id param
# ------FOR ETHERNET INTERFACES------
# {
#     'ethintf': {
#             'type': 'EthIntf',
#              'id': {
#                  'shelf': '1',
#                  'card': '1',
#                  'ethintf': '1'}
#              }
#  }
create_e7_data.vlan_members(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    vlan_member_id="0",
    int_id={"ethintf": {"type": "EthIntf", "id": {"shelf": "1", "card": "1", "ethintf": "1"}}},
)


# ------FOR ERPS/G8032 RINGS------
# {
#     'eapsintf': {
#         'type': 'EapsIntf',
#         'id': {'eapsintf':'1'
#               }
#     }
# }
create_e7_data.vlan_members(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    vlan_member_id="0",
    int_id={"eapsintf": {"type": "EapsIntf", "id": {"eapsintf": "1"}}},
)
# ------FOR LAG INTERFACES------
# {
#     'lagintf': {
#             'type': 'LagIntf',
#              'id': {
#                  'lagintf': '1'
#                 }
#              }
# }
create_e7_data.vlan_members(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    vlan_member_id="0",
    int_id={"lagintf": {"type": "LagIntf", "id": {"lagintf": "1"}}},
)
