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

# Once the Query_E7_Data() object is created we can then call the show_ont() function
# show_ont() function can be used to collect the Provisioned ONTs Data on the targeted Network Name(ie..the E7 NODE)
# -----IMPORTANT NOTE-----
# While testing this solution, I discovered a http_timeout of 5, had to be set to prevent a timeout, your mileage may vary

# this base query will pull data for all provisioned ONTs on the targeted Network Name(ie..the E7 NODE)
query_e7_data.show_ont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    http_timeout=5,
)

# While pulling data for all ONTs on the node can be useful, it is much better to have a more precise query
# for this we can pass filters to the show_ont() function
# ---------LIST OF FILTERS----------
# admin:['enabled', 'enabled-no-alarms', 'disabled']
# serno:'123456'
# subscr-id: '99999'
# reg-id:
# pon:{'shelf': '1', 'card': '1', 'gponport': '1'}
# ontprof: '1'
# ont:'1'

# In this example we will pull the stats for all provisioned ONTs that are 'enabled'
query_e7_data.show_ont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    http_timeout=5,
    action_args={"admin": "enabled"},
)

# In this example we will pull the stats for all provisioned ONTs using a specific ontprof
# IMPORTANT NOTE - submit the ontprof id not the name
query_e7_data.show_ont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    http_timeout=5,
    action_args={"ontprof": "1"},
)

# In this example we will pull the stats for all provisioned ONTs that are on a specific pon port
# for this example we will be using GPON id 1/1/1
query_e7_data.show_ont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    http_timeout=5,
    action_args={"pon": {"shelf": "1", "card": "1", "gponport": "1"}},
)

# In this example we will pull the stats for the specified ONT by its serial-number
# IMPORTANT NOTE - cms expects the Hexadecimal version of the SN, normally this will be the last 6 char of the serial
# Say we have a serial of CXNK00123456, we would submit 123456
query_e7_data.show_ont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    http_timeout=5,
    action_args={"serno": "123456"},
)

# In this example we will pull the stats for the specified ONT by its provisioned subscriber-id
query_e7_data.show_ont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    http_timeout=5,
    action_args={"subscr-id": "99999999"},
)

# In this example we will pull the stats for the specified ONT by its ONT ID
query_e7_data.show_ont(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example Network Name",
    http_timeout=5,
    action_args={"ont": "1"},
)
