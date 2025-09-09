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

# Once the Query_E7_Data object is created we can then call the ont_children_ethsvc() function

# ALL EthSvc on the specified ONT_ID
query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
)

# We can also pass filters to ont_children_ethsvc() function to narrow our query down.
# --------------LIST OF FILTERS--------------
# --------KEY--------|--------VALUE--------
# 'admin'            | 'enabled' or 'disabled' or 'enabled-no-alarms'
# 'descr'            | 'example_description'
# 'tag-action'       | {'type': 'SvcTagAction', 'id': {'svctagaction': 'svctagaction_id'}}
# 'bw-prof'          | {'type': 'BwProf', 'id': {'bwprof': 'bwprof_id'}}
# 'out-tag'          | 'none' or '2' --------s-tag, ie outer tag of a QinQ frame should be represented as an int str object
# 'in-tag'           | 'none' or '2' --------c-tag, ie inner tag of a QinQ frame should be represented as an int str object
# 'mcast-prof'       | None or {'type': 'McastProf', 'id': {'mcastprof': 'mcastprof_id'}}
# 'pon-cos'          | 'derived' or 'cos-1' through 'cos-4' or 'user-1' through 'user-4' or 'fixed' ----Please reference pg.173 from (Calix Management System (CMS) R15.x Northbound Interface API Guide) && pg.251 from (Calix E-Series (E7 OS R2.5) Engineering and Planning Guide) for more information
# 'us-cir-override'  | 'none' or '1k' through '2048k' in 64bit increments or '0m' through '2500m'   ----Please reference pg.205-310 from (Calix E-Series (E7 OS R2.5) Engineering and Planning Guide) for more information
# 'us-pir-override'  | 'none' or '1k' through '2048k' in 64bit increments or '0m' through '2500m'   ----Please reference pg.205-310 from (Calix E-Series (E7 OS R2.5) Engineering and Planning Guide) for more information
# 'ds-pir-override'  | 'none' or '1k' through '2048k' in 64bit increments or '0m' through '2500m'   ----Please reference pg.205-310 from (Calix E-Series (E7 OS R2.5) Engineering and Planning Guide) for more information
# 'hot-swap'         | 'enabled' or 'disabled' -----Please reference (Calix E-Series (E7 EXA R3.x) GPON Applications Guide) for more information


# ------BY ADMIN STATE------
query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
    attr_filter={"admin": "enabled"},
)

# ------BY EthSvc DESCRIPTION------
query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
    attr_filter={"descr": "example_description"},
)

# ------BY SvcTagAction ID------
query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
    attr_filter={"tag-action": {"type": "SvcTagAction", "id": {"svctagaction": "1"}}},
)

# ------BY BANDWIDTH PROFILE ID------
query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
    attr_filter={"bw-prof": {"type": "BwProf", "id": {"bwprof": "1"}}},
)

# ------BY OUTER VLAN TAG------
query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
    attr_filter={"out-tag": "2"},
)

# ------BY INNER VLAN TAG------
query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
    attr_filter={"in-tag": "2"},
)

# ------BY MULTICAST PROFILE ID------
query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
    attr_filter={"mcast-prof": {"type": "McastProf", "id": {"mcastprof": "1"}}},
)

query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
    attr_filter={"mcast-prof": None},
)


# ------BY PON COS------
query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
    attr_filter={"pon-cos": "derived"},
)

query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
    attr_filter={"pon-cos": "cos-1"},
)

query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
    attr_filter={"pon-cos": "user-1"},
)

query_e7_data.ont_children_ethsvc(
    message_id="1",
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    network_nm="NTWK-Example_Name",
    http_timeout=1,
    ont_id="1",
    attr_filter={"pon-cos": "fixed"},
)
