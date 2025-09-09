# IMPORT STATEMENT
from CMSNBIClient import CMS_NBI_Client, Delete_E7_Data

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

# Next we create a Delete_E7_Data instance and pass the CMS_NBI_Client instance to it
delete_e7_data = Delete_E7_Data(client)

# once the Delete_E7_Data() object is created we can then call the ont() function
# there are two ways to submit the ont() function

# 1st METHOD
# -----IMPORTANT NOTE-----
# This method will delete the ont and any services built on the ont_id specified
delete_e7_data.ont(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    ont_id="1",
    force="true",
)
# 2nd METHOD
# -----IMPORTANT NOTE-----
# This method will require that all services be removed from the ont_id specified before submitting to delete it
delete_e7_data.ont(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    ont_id="1",
    force="false",
)
