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

# once the Query_E7_Data() object is created we can then call the system_children_discont() function
# system_children_discont() function can be used to collect the Discovered ONTS on the targeted Network Name(ie..the E7 NODE)
# this base query will pull all Discovered ONTs, whether they are provisioned or not
query_e7_data.system_children_discont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    message_id="1",
)

# we can also pass filters to narrow down the selection of Discovered ONTS
# ---------LIST OF FILTERS----------
# alt-cust-vers: ,
# alt-sw-vers: '12.0.0.0.1',
# clei: '0000000000',
# crit: '0',
# curr-committed: 'true',
# curr-cust-vers: None,
# curr-sw-vers: '12.0.0.0.1',
# derived-states: 'default-prov',
# descr: 'description',
# info: '0',
# link-permit-status: 'ok-calix',
# 'maj': '0',
# 'mfg-serno': '000000000000',
# 'min': '0',
# 'model': '812G-1',
# 'mta-mac': '00:00:00:00:00:00',
# 'ont': '0',
# 'ontprof': None,
# 'onu-mac': '00:00:00:00:00:00',
# 'op-stat': 'enable',
# 'pon': {'card': '1', 'gponport': '1', 'shelf': '1'},
# 'product-code': 'P2',
# 'prov-reg-id': None,
# 'reg-id': '99999999',
# 'subscr-id': '999999',
# 'type': 'DiscOnt',
# 'vendor': 'CXNK',
# 'warn': '0'}]
# this example selects all onts that do not have provisioning
query_e7_data.system_children_discont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    attr_filter={"ont": "0"},
    message_id="1",
)

# this example selects all onts that do not have provisioning, and are of the 812G-1 model
query_e7_data.system_children_discont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    attr_filter={"ont": "0", "model": "812G-1"},
    message_id="1",
)

# this example selects all onts that do not have provisioning, and are on pon_id 1/1/1
query_e7_data.system_children_discont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    attr_filter={"ont": "0", "pon": {"shelf": "1", "card": "1", "gponport": "1"}},
    message_id="1",
)

# If you are wanting to check if a specific ONT is Discovered on the targeted Network Name(ie..the E7 NODE)
# We can use the discont() function
query_e7_data.discont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    ont_sn="CXNK123456",
)

# unlike system_children_discont() discont() will return a dict on a successful call and not a list of dicts
