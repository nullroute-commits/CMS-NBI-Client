# IMPORT STATEMENT
from CMSNBIClient import CMS_NBI_Client, Query_Rest_Data

# IMPORT STATEMENT

# Create the CMS_NBI_Client() instance
client = CMS_NBI_Client()

# While the Query_E7_Data interacts with CMS' NETCONF interface, Query_Rest_Data interacts with CMS REST interface and
# returns the data in a json format

# Next we create a Query_Rest_Data instance and pass the CMS_NBI_Client instance to it
query_rest_data = Query_Rest_Data(client)

# Once the Query_Rest_Data() instance is created we can call the device() function to query for all nodes with the matching device type

# QUERY FOR E7 Nodes
query_rest_data.device(
    protocol="http",
    port="8080",
    cms_user_nm=client.cms_nbi_config["example_node"]["cms_creds"]["user_nm"],
    cms_user_pass=client.cms_nbi_config["example_node"]["cms_creds"]["pass_wd"],
    cms_node_ip=client.cms_nbi_config["example_node"]["cms_nodes"]["example_node"]["connection"][
        "cms_node_ip"
    ],
    device_type="e7",
    http_timeout=5,
)

# QUERY FOR C7 Nodes
query_rest_data.device(
    protocol="http",
    port="8080",
    cms_user_nm=client.cms_nbi_config["example_node"]["cms_creds"]["user_nm"],
    cms_user_pass=client.cms_nbi_config["example_node"]["cms_creds"]["pass_wd"],
    cms_node_ip=client.cms_nbi_config["example_node"]["cms_nodes"]["example_node"]["connection"][
        "cms_node_ip"
    ],
    device_type="c7",
    http_timeout=5,
)
