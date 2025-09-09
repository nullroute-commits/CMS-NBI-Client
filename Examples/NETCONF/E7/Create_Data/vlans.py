# IMPORT STATEMENT
import cmsnbiclient

# IMPORT STATEMENT

# Create the CMS_NBI_Client() instance
client = cmsnbiclient.Client()

# Next step is to submit a login request to the CMS server, I will be using an example node
login_resp = client.login_netconf(
    cms_user_nm=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["user_nm"],
    cms_user_pass=client.cms_nbi_config["cms_nodes"]["example_node"]["cms_creds"]["pass_wd"],
    cms_node_ip=client.cms_nbi_config["cms_nodes"]["example_node"]["connection"]["cms_node_ip"],
    uri=client.cms_nbi_config["cms_netconf_uri"]["e7"],
)
# if the login_netconf() function is successful '0' is returned  else a response.Models.Response object is returned
# you can use the response library to debug the response.models.response object
if isinstance(login_resp, str):
    pass
else:
    print(login_resp.content)
    raise "ERROR LOGGING IN"
# Assigning the network_nm str
network = "NTWK-Example_Name"

# Next we create a Create_E7_Data instance and pass the CMS_NBI_Client instance to it
create_ncf = cmsnbiclient.E7.Create(client, network_nm=network, http_timeout=5)

# Once the Create_E7_Data object is created we can then call the vlan function and create a vlan with the provided parameters
#################################################################################################################
# CREATE DEFAULT VLAN PER DOCUMENTATION IN pg.335-338 Calix E-Series (E7 OS R2.5) Engineering and Planning Guide
create_ncf.vlan(vlan_id="15", name="Example_VLAN")

# CREATE A TLAN USED FOR MEF E-Line,E-LAN, E-TREE circuits
create_ncf.vlan(vlan_id="15", name="Example_TLAN", pon_tlan="true")

# CREATE A VLAN USED FOR SERVING PPPOE TRAFFIC USING PPPOE_PROFILE WITH AN ID OF 1
create_ncf.vlan(
    vlan_id="15",
    name="Example_PPPOE_VLAN",
    pppoe_profile={"pppoe-prof": {"type": "PppoeProf", "id": {"pppoeprof": "1"}}},
)

# CREATE A VLAN USED FOR SERVING HSI DHCP SERVICES WITHOUT USING A DHCP_SERVICE
create_ncf.vlan(vlan_id="15", name="Example_Basic_DHCP", dhcp_mode="snoop")

# CREATE A VLAN USED FOR SERVING HSI DHCP SERVICES USING THE DHCP_SERVICE WITH A PROFILE ID OF 1
create_ncf.vlan(
    vlan_id="15",
    name="Example_Complex_DHCP",
    dhcp_mode="proxy",
    dhcp_svc_profile={"dhcp-svc-prof": {"type": "DhcpSvcProf", "id": {"dhcpsvcprof": "1"}}},
)
