# IMPORT STATEMENT
from CMSNBIClient import CMS_NBI_Client, Update_E7_Data

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

# Next we create an Update_E7_Data instance and pass the CMS_NBI_Client instance to it
update_e7_data = Update_E7_Data(client)
# Once the Update_E7_Data object is created we can then call the ont() function and update ont variables for a specific ont
# For any updated query an ont_id must be provided in the ont_id var
# Only the var being updated needs to be supplied

# Updating the ont 1 admin_state>>disabled
update_e7_data.ont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Network",
    ont_id="1",
    admin_state="disabled",
)

# Updating the ont 2 Subscriber Id  && Description
update_e7_data.ont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Network",
    ont_id="2",
    sub_id="9999999",
    ont_desc="example_ont",
)

# Updating ont 4 to False on the battery_present
update_e7_data.ont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Network",
    ont_id="4",
    battery_present="false",
)

# Replace an ONT with a new ont
# this requires two calls one to unlink the cxnk and another to link a new cxnk
update_e7_data.ont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Network",
    ont_id="4",
    ont_sn="0",
    replace_sn="1",
)

update_e7_data.ont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Network",
    ont_id="4",
    ont_sn="9999",
)
