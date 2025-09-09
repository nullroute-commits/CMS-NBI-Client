# IMPORT STATEMENTS
import random

import pydash
import requests
import xmltodict

from ..client import Client  # Import Client from relative path to avoid circular import

# IMPORT STATEMENTS


class Create:
    def __init__(self, client_object: Client, network_nm: str = "", http_timeout: int = 1):
        """
        Description
        -----------
        Class (Create) is the creation query constructor/posting class for the E7 CMS NETCONF NBI

        Attributes
        ----------
        :param client_object:accepts object created by the cms_nbi_client.client.Client()
        :type client_object:Client

        :param network_nm:this parameter contains the node name, which is made of the case-sensitive name of the E7 OS platform, preceded by NTWK-. Example: NTWK-Pet02E7. The nodename value can consist of alphanumeric, underscore, and space characters, this is described in pg.26 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type network_nm:str

        :param http_timeout:this parameter is fed to the request.request() function as a timeout more can be read at the request library docs
        :type http_timeout:int

        :var self.message_id:a positive int up to 32bit is generated with each call of self.message_id, the CMS server uses this str to match requests/responses, for more infomation please read pg.29 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type self.message_id:str

        :var self.client_object:accepts object created by the cmsnbiclient.client.Client()
        :type self.client_object:object

        :raises:
            ValueError: Will be raised if the object provided is not of cmsnbiclient.client.Client()
            ValueError: Will be raised if the network_nm is not a str with a length at least 1 char
        """
        # Test if the provided object is of a Client instance or CMSClient
        # Import at runtime to avoid circular imports
        from ..client_v2 import CMSClient

        if isinstance(client_object, (Client, CMSClient)):
            pass
        else:
            raise ValueError(
                f"""Create() accepts a instance of cmsnbiclient.client.Client() or CMSClient, a instance of {type(client_object)} was passed"""
            )
        self.client_object = client_object
        # Test if the cms_netconf_url is a str object and contains the e7 uri
        if isinstance(self.client_object.cms_netconf_url, str):
            if (
                self.client_object.cms_nbi_config["cms_netconf_uri"]["e7"]
                in self.client_object.cms_netconf_url
            ):
                pass
            else:
                raise ValueError(
                    f"""uri:{self.client_object.cms_nbi_config['cms_netconf_uri']['e7']} was not found in self.client_object.cms_netconf_url:{self.client_object.cms_netconf_url}"""
                )
        else:
            raise ValueError(f"""self.client_object.cms_netconf_url must be a str object""")
        # TEST THE SESSION_ID VAR, THIS INSURES THAT ANY REQUEST ARE GOOD TO AUTHED
        if isinstance(self.client_object.session_id, str):
            if self.client_object.session_id.isdigit():
                pass
            else:
                raise ValueError(f"""self.client_object.session_id must be a int in a str object""")
        else:
            raise ValueError(f"""self.client_object.session_id must be a str object""")
        # TEST IF THE NETWORK_NM is an empty string
        if isinstance(network_nm, str):
            if len(network_nm) >= 1:
                pass
            else:
                raise ValueError(f"""network_nm cannot be an empty str""")
        else:
            raise ValueError(f"""network_nm must be a str""")
        # END PARAMETER TEST BLOCK

        # ASSIGNING CLASS VARIABLES
        self.network_nm = network_nm
        self.http_timeout = http_timeout

    @property
    def message_id(self):
        """
        Description
        -----------
        :var self.message_id: a positive 32bit int is generated with each call of self.message_id, the CMS server uses this str to match requests/responses, for more infomation please read pg.29 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :return: self.message_id
        """
        return str(random.getrandbits(random.randint(2, 31)))

    @property
    def headers(self):
        """
        Description
        -----------
        :var self.headers: a positive 32bit int is generated with each call of self.message_id, the CMS server uses this str to match requests/responses, for more infomation please read pg.29 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :return: self.headers
        """
        return {
            "Content-Type": "text/xml;charset=ISO-8859-1",
            "User-Agent": f"CMS_NBI_CONNECT-{self.cms_user_nm}",
        }

    @property
    def cms_user_nm(self):
        return self.client_object.cms_user_nm

    def ont(
        self,
        ont_id="0",
        admin_state="enabled",
        ont_sn="0",
        reg_id="",
        sub_id="",
        ont_desc="",
        ontpwe3prof_id="1",
        ontprof_id="",
        us_sdber_rate="5",
        low_rx_opt_pwr_ne_thresh="-30.0",
        high_rx_opt_pwr_ne_thresh="-7.0",
        battery_present="false",
        pse_max_power_budget="30",
        poe_class_control="disabled",
    ):
        """
        Description
        -----------
        function ont() performs a http/xml creation query for the provided network_nm(e7_node) requesting an <Ont> object be created with the provided details

        Attributes
        ----------
        :param ont_id:Identifies the ONT by its E7 scope ID (1 to 64000000), submitting '0' requests the ont be built on the first available ID, as described in pg.129 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type ont_sn:str

        :param admin_state:operational status of the created ONT, valid values are [disabled,enabled,enabled-no-alarms], this is explained further in pg.237 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type admin_state:str

        :param ont_sn:identifies the Hexadecimal representation of the ONT serial number, to assign the SN at a later date, input '0', as described in pg.140 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type ont_sn:str

        :param reg_id:ONT registration ID that is the RONTA identifier., as described in pg.232 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type reg_id:str

        :param sub_id:Identifies the subscriber ID., as described in pg.63 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type sub_id:str

        :param ont_desc:Identifies the ONT Description
        :type ont_desc:str

        :param ontpwe3prof_id:identifies the ID of the profile that sets the ONT PWE3 mode. Use 1 (also the default, if not supplied) for the system-default profile, which is set to use either T1 or E1 mode in the management interface. as described in pg.141 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type ontpwe3prof_id:str

        :param ontprof_id:identifies the ID of a global or local ONT profile (1 to 50, or one of the default global profiles listed in Global ONT Profile IDs, as described in pg.282-285 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type ontprof_id:str

        :param us_sdber_rate:Also Known as (Upstream Signal Degraded Error Rate) identifies the threshold for upstream bit errors before an alarm is raised range (2-6), please see pg.31 of E-Series EXA R3.x Maintenance and Troubleshooting Guide for more information
        :type us_sdber_rate:str

        :param low_rx_opt_pwr_ne_thresh:Also known as (Low Receive Optical Power Near End Threshold) identifies the lowest optical signal level that the ONT will accept before raising a low-rx-opt-pwr-ne alarm, default value(-30.0) accepts(-30.0 to -7.0), please see pg.61 & pg.421 of E-Series EXA R3.x Maintenance and Troubleshooting Guide for more information
        :type low_rx_opt_pwr_ne_thresh:str

        :param high_rx_opt_pwr_ne_thresh:Also known as (High Receive Optical Power Near End Threshold) identifies the highest optical signal level that the ONT will accept before raising a high-rx-opt-pwr-ne alarm, default value(-7.0) accepts(-30.0 to -7.0) please see pg.61 & pg.421 of E-Series EXA R3.x Maintenance and Troubleshooting Guide for more information
        :type high_rx_opt_pwr_ne_thresh:str

        :param battery_present:Identifies the requested batter-present state ie(true or false), this will determine if the ont alarms once it identifies the commercial power has been cut, please see pg.532 of Calix E-Series (E7 OS R3.1/R3.2) Engineering and Planning Guide for more information
        :type battery_present:str

        :param pse_max_power_budget:This defines the Power Sourcing Equipment (PSE) maximum power budget in Watts that the OLT can source on all Power over Ethernet (PoE) enabled Ethernet UNI ports. The PSE maximum power budget is effective in ONT only if the ownership is OMCI. default value(30) accepts(1 to 90), please see  E7 EXA R3.x GPON Applications Guide for more information
        :type pse_max_power_budget:str

        :param poe_class_control:the port can be classified to the type of Powered Device (PD) that will be connected to the port. Different classes of PD require different amounts of power, accepts 'enabled' or 'disabled', please see pg.532 of Calix E-Series (E7 OS R3.1/R3.2) Engineering and Planning Guide for more information
        :type poe_class_control:str

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection between the client and server times-out

        :return: ont() returns a response.models.Response object on a failed call, and a nested dict on a successful call

        Example
        -----------
        # IMPORT STATEMENT
        import cmsnbiclient
        # IMPORT STATEMENT

        # Create the Client() instance
        client = cmsnbiclient.Client()

        # Next step is to submit a login request to the CMS server, I will be using an example node
        login_resp = client.login_netconf(cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          cms_user_pass=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['pass_wd'],
                                          cms_node_ip=client.cms_nbi_config['cms_nodes']['example_node']['connection']['cms_node_ip'],
                                          uri=client.cms_nbi_config['cms_netconf_uri']['e7'])
        # if the login_netconf() function is successful '0' is returned  else a response.Models.Response object is returned
        # you can use the response library to debug the response.models.response object
        if isinstance(login_resp, str):
            pass
        else:
            print(login_resp.content)
            raise 'ERROR LOGGING IN'
        # Assuming the login was successful we will assign a network name to a var for futher use
        network = 'NTWK-Example_Name'

        # Next we create a Create() instance and pass the cmsnbiclient.client.Client() instance to it
        create_ncf = cmsnbiclient.E7.Create(client, network_nm=network, http_timeout=5)
        # Once the Create_E7_Data object is created we can then call the ont() function and create a new ont record

        # When creating an ONT we have a plethora of variables and combination to leverage. I will provide examples for some ONT configurations that I personally use day to day.
        # THE DEFAULT CMS SERVER CONTAINS A GROUP OF DEFAULT ONT-PROFILES THAT CAN BE USED TO FILL THE ontprof_id variable.
        # These profiles can be found on pg.136 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        # these profiles are the default and new custom profiles can be created to meet network design requirements.

        # CREATE A DEFAULT 812G ONT, USING THE FIRST ONT_ID available on NTWK-Example_Name.
        # Coupled with ont_sn='0', this call will tell the cms server to create a new ont record with no SN allowing us to fill it in later.
        create_ncf.ont(ont_id='0',
                       admin_state='enabled',
                       ont_sn='0',
                       reg_id='',
                       sub_id='999999',
                       ont_desc='Example_Description',
                       ontpwe3prof_id='1',
                       ontprof_id='162')

        # CREATE A DEFAULT 812G ONT, USING THE FIRST ONT_ID AVAILABLE ONT NTWK-Example_Name
        # With this call we provided the ONT_SN, this will create a record tying the ONT_SN to the ONT provisioning, once the ont is discovered by the E7 the config is pushed.
        create_ncf.ont(ont_id='0',
                       admin_state='enabled',
                       ont_sn='0',
                       reg_id='',
                       sub_id='999999',
                       ont_desc='Example_Description',
                       ontpwe3prof_id='1',
                       ontprof_id='162')
        """

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <edit-config>
                                    <target>
                                        <running/>
                                    </target>
                                    <config>
                                        <top>
                                            <object operation="create" get-config="true">
                                                <type>Ont</type>
                                                <id>
                                                    <ont>{ont_id}</ont>
                                                </id>
                                                <admin>{admin_state}</admin>
                                                <serno>{ont_sn}</serno>
                                                <reg-id>{reg_id}</reg-id>
                                                <subscr-id>{sub_id}</subscr-id>
                                                <descr>{ont_desc}</descr>
                                                <pwe3prof>
                                                    <type>OntPwe3Prof</type>
                                                    <id>
                                                        <ontpwe3prof>{ontpwe3prof_id}</ontpwe3prof>
                                                    </id>
                                                </pwe3prof>
                                                <ontprof>
                                                    <type>OntProf</type>
                                                    <id>
                                                        <ontprof>{ontprof_id}</ontprof>
                                                    </id>
                                                </ontprof>
                                                <us-sdber-rate>{us_sdber_rate}</us-sdber-rate>
                                                <low-rx-opt-pwr-ne-thresh>{low_rx_opt_pwr_ne_thresh}</low-rx-opt-pwr-ne-thresh>
                                                <high-rx-opt-pwr-ne-thresh>{high_rx_opt_pwr_ne_thresh}</high-rx-opt-pwr-ne-thresh>
                                                <battery-present>{battery_present}</battery-present>
                                                <pse-max-power-budget>{pse_max_power_budget}</pse-max-power-budget>
                                                <poe-class-control>{poe_class_control}</poe-class-control>
                                            </object>
                                        </top>
                                    </config>
                                </edit-config>
                            </rpc>
                        </soapenv:Body>
                    </soapenv:Envelope>"""

        if "https" not in self.client_object.cms_netconf_url:
            try:
                response = requests.post(
                    url=self.client_object.cms_netconf_url,
                    headers=self.headers,
                    data=payload,
                    timeout=self.http_timeout,
                )
            except requests.exceptions.Timeout as e:
                raise e
        else:
            # will need to research how to implement https connection with request library
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response object is returned.
            return response

        else:
            resp_dict = xmltodict.parse(response.content)
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object"
            ):
                return resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"]["top"][
                    "object"
                ]
            else:
                return response

    def vlan(
        self,
        vlan_id="",
        name="",
        igmp_mode="flood",
        vlanigmpprof_id="1",
        dhcp_mode="none",
        mac_force_forw="false",
        ip_src_verify="false",
        mac_learn="true",
        ae_ont_discovery="false",
        pon_tlan="false",
        pon_hairpin="false",
        igmp_pbit="pbit-4",
        dhcp_svc_profile={"dhcp-svc-prof": ""},
        option82_enable="true",
        eth_opt82prof_id="2",
        gpon_opt82prof_id="1",
        mobility="false",
        pppoe_profile={"pppoe-prof": ""},
    ):
        """
        Description
        -----------
        function vlan() performs a http/xml creation query for the provided network_nm(e7_node) requesting an <Vlan> object be created with the provided details

        Attributes
        ----------
        :param vlan_id: Identifies the VLAN: 2 to 4093 (Except for 1002-1005 which are reserved for E7 operation.), excluding any reserved VLANs as described in pg.50 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type vlan_id:str

        :param name:Identifies the name of the VLAN. Spaces and special characters are permitted. as described in pg.43 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type name:str

        :param igmp_mode: Identifies the igmp_mode used by the e7 node to treat mcast traffic on the vlan, as described in pg.43 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type igmp_mode:str

        :param vlanigmpprof_id: Numerical identifier for the local profile (1 to 20), The local IGMP profile ID can be viewed in the management interface. In the IGMP profile list, double-click a profile to view its ID above the Name field.  If <igmp-prof> is not specified, the systemdefault IGMP profile (1) is used.  this is described in pg.43 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type vlanigmpprof_id:str

        :param dhcp_mode: this setting enables or disabled dhcp snooping on the vlan, as described in pg.43 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type dhcp_mode:str

        :param mac_force_forw:this setting enables or disabled mac_force_forwarding on the vlan, as described in pg.43 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type mac_force_forw:str

        :param ip_src_verify: enable or disables IP source verification (binding the IP and MAC addresses to the physical ONT Ethernet port), as described in pg.43 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type ip_src_verify:str

        :param mac_learn: enables or disables mac-learning on the vlan, "Only applicable for E7-20 and E7-2 standalone systems; Modular Chassis configurations only support MAC learning", as described in pg.43 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type mac_learn:str

        :param ae_ont_discovery: enables or disables ae-ont-discovery, (Only supported when DHCP snooping is enabled, as described in pg.43 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type ae_ont_discovery:str

        :param pon_tlan: enables or disables pon-tlan perameter, as described in pg.43 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type pon_tlan:str

        :param pon_hairpin:(Applicable for TLAN and T1/E3 PWE3 services) this allows for traffic to be hair-pin back to the same olt on a differing or same uni, this is explained better in pg.337 of Calix E-Series (E7 OS R2.5) Engineering and Planning Guide
        :type pon_hairpin:str

        :param igmp_pbit: The P-bit value(pbit-0 through pbit-7) for IGMP traffic that passes through the system, allowing the traffic type to be treated differently as it passes through the network. this is explained better in pg.337 of Calix E-Series (E7 OS R2.5) Engineering and Planning Guide
        :type igmp_pbit:str

        :param dhcp_svc_profile:Required for the configuration of DHCPv4 Proxy (Layer 3 DHCP Relay) on the client-side VLAN,The selected profile determines the DHCP Proxy Agent IP interface and IP address of the DHCP server(s). this is explained better in pg.337 of Calix E-Series (E7 OS R2.5) Engineering and Planning Guide
        :type dhcp_svc_profile:dict

        :param option82_enable:Enables or disables Option 82/LDRA at the VLAN level
        :type option82_enable:str

        :param eth_opt82prof_id:Access Identifier Profile for Ethernet/xDSL subscribers, specifying the Circuit and Remote ID format for Option 82 content insertion, this is explained better in pg.337 of Calix E-Series (E7 OS R2.5) Engineering and Planning Guide
        :type eth_opt82prof_id:str

        :param gpon_opt82prof_id:Access Identifier Profile for GPON subscribers, specifying the Circuit and Remote ID format for Option 82 content insertion, this is explained better in pg.337 of Calix E-Series (E7 OS R2.5) Engineering and Planning Guide
        :type gpon_opt82prof_id:str

        :param mobility:Enables or disables the ability for client devices to move freely between different ONTs on the same PON or card. (Not supported across multiple cards, this is explained better in pg.338 of Calix E-Series (E7 OS R2.5) Engineering and Planning Guide
        :type mobility:str

        :param pppoe_profile:Assign a previously-created PPPoE profile. When a PPPoE profile is selected, the DHCP features are disabled. Setting a VLAN PPPoE profile to “none” passes through all PPPoE traffic, transparently. If a PPPoE profile is used with PPPoE snoop, a list of all the active sessions and statistics are available, and the PPPoE stack is enabled, which passes through PPPoE traffic transparently as long as the Clients/BRAS are operating normally (illegal packets will be dropped),this is explained better in pg.338 of Calix E-Series (E7 OS R2.5) Engineering and Planning Guide
        :type pppoe_profile:dict

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: vlan() function will return a dict on a success`full call, and a request.Models.Response object on a failed call

        Example
        -----------
        # IMPORT STATEMENT
        import cmsnbiclient
        # IMPORT STATEMENT

        # Create the CMS_NBI_Client() instance
        client = cmsnbiclient.Client()

        # Next step is to submit a login request to the CMS server, I will be using an example node
        login_resp = client.login_netconf(cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          cms_user_pass=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['pass_wd'],
                                          cms_node_ip=client.cms_nbi_config['cms_nodes']['example_node']['connection']['cms_node_ip'],
                                          uri=client.cms_nbi_config['cms_netconf_uri']['e7'])
        # if the login_netconf() function is successful '0' is returned  else a response.Models.Response object is returned
        # you can use the response library to debug the response.models.response object
        if isinstance(login_resp, str):
            pass
        else:
            print(login_resp.content)
            raise 'ERROR LOGGING IN'
        # Assigning the network_nm str
        network = 'NTWK-Example_Name'

        # Next we create a Create_E7_Data instance and pass the CMS_NBI_Client instance to it
        create_ncf = cmsnbiclient.E7.Create(client, network_nm=network, http_timeout=5)

        # Once the Create_E7_Data object is created we can then call the vlan function and create a vlan with the provided parameters
        #################################################################################################################
        # CREATE DEFAULT VLAN PER DOCUMENTATION IN pg.335-338 Calix E-Series (E7 OS R2.5) Engineering and Planning Guide
        create_ncf.vlan(vlan_id='15', name='Example_VLAN')

        # CREATE A TLAN USED FOR MEF E-Line,E-LAN, E-TREE circuits
        create_ncf.vlan(vlan_id='15',
                        name='Example_TLAN',
                        pon_tlan='true')

        # CREATE A VLAN USED FOR SERVING PPPOE TRAFFIC USING PPPOE_PROFILE WITH AN ID OF 1
        create_ncf.vlan(vlan_id='15',
                        name='Example_PPPOE_VLAN',
                        pppoe_profile={'pppoe-prof': {'type': 'PppoeProf', 'id': {'pppoeprof': '1'}}})

        # CREATE A VLAN USED FOR SERVING HSI DHCP SERVICES WITHOUT USING A DHCP_SERVICE
        create_ncf.vlan(vlan_id='15',
                        name='Example_Basic_DHCP',
                        dhcp_mode='snoop')

        # CREATE A VLAN USED FOR SERVING HSI DHCP SERVICES USING THE DHCP_SERVICE WITH A PROFILE ID OF 1
        create_ncf.vlan(vlan_id='15',
                        name='Example_Complex_DHCP',
                        dhcp_mode='proxy',
                        dhcp_svc_profile={'dhcp-svc-prof': {'type': 'DhcpSvcProf', 'id': {'dhcpsvcprof': '1'}}})

        """
        if isinstance(pppoe_profile["pppoe-prof"], dict):
            _pppoe_profile = xmltodict.unparse(pppoe_profile, full_document=False)
        else:
            _pppoe_profile = """<pppoe-prof></pppoe-prof>"""

        if isinstance(dhcp_svc_profile["dhcp-svc-prof"], dict):
            _dhcp_svc_prof_id = xmltodict.unparse(dhcp_svc_profile, full_document=False)
        else:
            _dhcp_svc_prof_id = """<dhcp-svc-prof></dhcp-svc-prof>"""

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <edit-config>
                                    <target>
                                        <running/>
                                    </target>
                                    <config>
                                        <top>
                                            <object operation="create" get-config="true">
                                                <type>Vlan</type>
                                                <id>
                                                    <vlan>{vlan_id}</vlan>
                                                </id>
                                                <name>{name}</name>
                                                <igmp-mode>{igmp_mode}</igmp-mode>
                                                <igmp-prof>
                                                    <type>VlanIgmpProf</type>
                                                    <id>
                                                        <vlanigmpprof>{vlanigmpprof_id}</vlanigmpprof>
                                                    </id>
                                                </igmp-prof>
                                                <dhcp-mode>{dhcp_mode}</dhcp-mode>
                                                <mac-force-forw>{mac_force_forw}</mac-force-forw>
                                                <ip-src-verify>{ip_src_verify}</ip-src-verify>
                                                <mac-learn>{mac_learn}</mac-learn>
                                                <ae-ont-discovery>{ae_ont_discovery}</ae-ont-discovery>
                                                <pon-tlan>{pon_tlan}</pon-tlan>
                                                <pon-hairpin>{pon_hairpin}</pon-hairpin>
                                                <igmp-pbit>{igmp_pbit}</igmp-pbit>
                                                {_dhcp_svc_prof_id}
                                                <option82-enable>{option82_enable}</option82-enable>
                                                <eth-opt82prof>
                                                    <type>Opt82Prof</type>
                                                    <id>
                                                        <opt82prof>{eth_opt82prof_id}</opt82prof>
                                                    </id>
                                                </eth-opt82prof>
                                                <gpon-opt82prof>
                                                    <type>Opt82Prof</type>
                                                    <id>
                                                        <opt82prof>{gpon_opt82prof_id}</opt82prof>
                                                    </id>
                                                </gpon-opt82prof>
                                                <mobility>{mobility}</mobility>
                                                {_pppoe_profile}
                                            </object>
                                        </top>
                                    </config>
                                </edit-config>
                            </rpc>
                        </soapenv:Body>
                    </soapenv:Envelope>"""

        if "https" not in self.client_object.cms_netconf_url:
            try:
                response = requests.post(
                    url=self.client_object.cms_netconf_url,
                    headers=self.headers,
                    data=payload,
                    timeout=self.http_timeout,
                )
            except requests.exceptions.Timeout as e:
                raise e
        else:
            # will need to research how to implement https connection with request library
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response object is returned.
            return response

        else:
            resp_dict = xmltodict.parse(response.content)
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object"
            ):
                return resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"]["top"][
                    "object"
                ]
            else:
                return response

    def vlan_members(self, vlan_id="", vlan_member_id="0", int_id={" ": ""}):
        """
        Description
        -----------
        function vlan_members() performs a http/xml creation query for the provided network_nm(e7_node) requesting an <VlanMem> object be created with the provided details

        Attributes
        ----------
        :param vlan_id:  Identifies the VLAN: 2 to 4093 (Except for 1002-1005 which are reserved for E7 operation.), excluding any reserved VLANs as described in pg.50 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type vlan_id:str

        :param vlan_member_id: —Identifies the VLAN member. Use one of the following: 0—The E7 auto-generates the VLAN member ID. 1 to 1000—Supply the VLAN member ID to use (must be unique). as described in pg.50 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type vlan_member_id:str

        :param int_id: identifies the interface object being added to the vlan object, please review pg.50 of Calix Management System (CMS) R15.x Northbound Interface API Guide for more information
        :type int_id:dict

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: vlan_members() will return a dict on a successfull query and a response.models.response object on a failed query

        Example
        -----------
        IMPORTANT NOTE

        You will need to submit the correct structured dictionary to the int_id param

        ------FOR ETHERNET INTERFACES------
        {
            'ethintf': {
                    'type': 'EthIntf',
                     'id': {
                         'shelf': '1',
                         'card': '1',
                         'ethintf': '1'}
                     }
         }
        Create_E7_Data.vlan_members(message_id='1',
                                    cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                    network_nm='NTWK-Example_Name',
                                    vlan_member_id='0',
                                    int_id={'ethintf': {
                                                'type': 'EthIntf',
                                                 'id': {
                                                     'shelf': '1',
                                                     'card': '1',
                                                     'ethintf': '1'}
                                                 }
                                            })

        ------FOR ERPS/G8032 RINGS------
        {
            'eapsintf': {
                'type': 'EapsIntf',
                'id': {'eapsintf':'1'
                      }
            }
        }
        Create_E7_Data.vlan_members(message_id='1',
                                    cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                    network_nm='NTWK-Example_Name',
                                    vlan_member_id='0',
                                    int_id={'eapsintf': {
                                                'type': 'EapsIntf',
                                                'id': {'eapsintf':'1'}
                                                        }
                                            })

        ------FOR LAG INTERFACES------
        {
            'lagintf': {
                    'type': 'LagIntf',
                     'id': {
                         'lagintf': '1'
                        }
                     }
        }
        Create_E7_Data.vlan_members(message_id='1',
                                    cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                    network_nm='NTWK-Example_Name',
                                    vlan_member_id='0',
                                    int_id={'lagintf': {
                                                        'type': 'LagIntf',
                                                         'id': {'lagintf': '1'}
                                                         }
                                            })
        """

        if " " not in int_id.keys() and len(int_id.keys()) == 1:
            if "ethintf" in int_id.keys():
                _int_id = xmltodict.unparse(int_id["ethintf"], full_document=False)
            elif "lagintf" in int_id.keys():
                _int_id = xmltodict.unparse(int_id["lagintf"], full_document=False)
            elif "eapsintf" in int_id.keys():
                _int_id = xmltodict.unparse(int_id["eapsintf"], full_document=False)
            else:
                raise AttributeError(
                    "int_id expects a object to add to the vlan_members please review and resubmit"
                )
        else:
            raise AttributeError(
                "int_id expects a object to add to the vlan_members please review and resubmit"
            )

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <edit-config>
                                    <target>
                                        <running/>
                                    </target>
                                    <config>
                                        <top>
                                            <object operation="create" get-config="true">
                                                <type>VlanMem</type>
                                                <id>
                                                    <vlan>{vlan_id}</vlan>
                                                    <vlanmem>{vlan_member_id}</vlanmem>
                                                </id>
                                                <member>
                                                    {_int_id}
                                                </member>
                                            </object>
                                        </top>
                                    </config>
                                </edit-config>
                            </rpc>
                        </soapenv:Body>
                    </soapenv:Envelope>"""

        if "https" not in self.client_object.cms_netconf_url:
            try:
                response = requests.post(
                    url=self.client_object.cms_netconf_url,
                    headers=self.headers,
                    data=payload,
                    timeout=self.http_timeout,
                )
            except requests.exceptions.Timeout as e:
                raise e
        else:
            # will need to research how to implement https connection with request library
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response object is returned.
            return response

        else:
            resp_dict = xmltodict.parse(response.content)
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]
                return resp_dict
            else:
                return response

    def ont_ethsvc(
        self,
        ont_id: str = "",
        ontslot: str = "3",
        ontethany: str = "1",
        ethsvc: str = "1",
        admin_state: str = "enabled",
        descr: str = "",
        svctagaction_id: str = "",
        bwprof_id: str = "",
        out_tag_id: str = "none",
        inner_tag_id: str = "none",
        mcast_prof_id: str = "0",
        pon_cos_id: str = "derived",
        us_cir_override: str = "none",
        us_pir_override: str = "none",
        ds_pir_override: str = "none",
        hot_swap: str = "false",
        pppoe_force_discard: str = "false",
    ):
        """
        Description
        -----------
        function ethsvc_ont() performs a http/xml creation query for the provided network_nm(e7_node) requesting an <ethsvc> object be created with the provided details

        Attributes
        ----------
        :param ont_id: Identifies the ONT by its E7 scope ID (1 to 64000000).

        :param ontslot: Identifies the ONT port type using one of the following {"Gigabit Ethernet port ": "3", "HPNA Ethernet port": "4", "Fast Ethernet port": "5" }

        :param ontethany: Identifies the ONT port number (1 to 8).

        :param ethsvc: Identifies the data service (1 to 12; typically 1 to 8 for data service).

        :param admin_state: Administrative status of the targeted ONT port (disabled, enabled, enabled-no-alarms).

        :param descr: Description of service.

        :param svctagaction_id: Identifies the ID of a predefined global service tag action (1 to 255).

        :param bwprof_id: Identifies the ID of a global or local Ethernet bandwidth profile (1 to 300). The CMS XML NBI may be used to provision services using local profile IDs. Previously, the CMS XML NBI accepted only global profile IDs.The local ID is specified using the syntax "local:X" where "X" is the local profile ID number.The local ID is specified using the syntax "local:X" where "X" is the local profile ID number.

        :param out_tag_id: "outer"(S-TAG) QinQ(802.1ad) VLAN IDs (2 to 4093, excluding any reserved VLAN IDs). Except for 1002-1005 which are reserved for E7 operation.

        :param inner_tag_id: "inner"(C-TAG) Dot1q(802.1Q) VLAN IDs (2 to 4093, excluding any reserved VLAN IDs). Except for 1002-1005 which are reserved for E7 operation.

        :param mcast_prof_id: Identifies an ID of a pre-defined global or local multicast profile (1 to 32). If provisioning as service not requiring mcast profile leave at default '0'. The CMS XML NBI may be used to provision services using local profile IDs. Previously, the CMS XML NBI accepted only global profile IDs.The local ID is specified using the syntax "local:X" where "X" is the local profile ID number. The local ID is specified using the syntax "local:X" where "X" is the local profile ID number.

        :param pon_cos_id: Class of Service applied to the service:
                             derived is the default behavior for services
                            created with E7 R2.2 or later.
                             cos-1 through cos-4 represents a default,
                            system-defined aggregated CoS for an ONT
                            (BE, AF1, AF2, EF) that are pre-assigned a
                            class of service and the provisioned services
                            are required to have a bandwidth profile that
                            matches the class of service. Bandwidth is
                            assigned as aggregated from the multiple
                            services and mapped to the ONT. If the
                            associated service-tag action was created with
                            a software version earlier than E7 software
                            release R2.2, the values of the selected
                            system-defined cos (1-4) override the
                            associated service-tag parameter selections.
                             user-1 through user-4 represents the PON
                            upstream profiles that specify the traffic class,
                            DBA scheduling priority, and bandwidth limits
                            for the service on the PON port.
                             fixed is the behavior that is the same as a
                            service created in a software version earlier
                            than E7 software release R2.2.

        :param us_cir_override: Overrides the provided bw_prof_id's upstream_CIR, Following the same syntax as bw_prof CIR provisioning.
                                Specifies the committed minimum rate the ONT allows traffic to flow
                                upstream. Where rates may be specified as follows:
                                 In 64 kbps increments up to 2 Mbps
                                 In 1 Mbps increments between 2 Mbps to 1000 Mbps
                                 In 100 Mbps increments between 1 Gbps to 1.2 Gbps
                                 0 kbps disables the meter
                                Use "m" suffix for Mb/s or "g" for Gb/s in whole number increments.
                                Note: 700GX ONTs can rate limit traffic to a maximum rate of 400
                                Mbps. Setting the rate limit for values higher than 400 Mbps will
                                disable the rate limiter.

        :param us_pir_override: Overrides the provided bw_prof_id's upstream_PIR, Following the same syntax as bw_prof PIR provisioning.
                                Specifies the un-guaranteed maximum rate for upstream traffic.
                                Where rates may be specified as follows:
                                 In 64 kbps increments up to 2 Mbps
                                 In 1 Mbps increments between 2 Mbps to 1000 Mbps
                                 0 kbps disables the meter
                                Use "m" suffix for Mbps or "g" for Gbps in whole number increments.
                                Note: 700GX ONTs can rate limit traffic to a maximum rate of 400
                                Mbps. Setting the rate limit for values higher than 400 Mbps
                                disables the rate limiter.

        :param ds_pir_override: Overrides the provided bw_prof_id's downstream_PIR, Following the same syntax as bw_prof PIR provisioning.
                                Specifies the maximum service bandwidth. Where rates may be
                                specified as follows:
                                 In 64 kbps increments up to 2 Mbps
                                 In 1 Mbps increments between 2 Mbps to 1000 Mbps
                                 In 100 Mbps increments between 1 Gbps to 2.5 Gbps
                                 0 kbps disables the meter
                                Use "m" suffix for Mbps or "g" for Gbps in whole number increments

        :param hot_swap: expects ('true' or 'false')
                            Provides a newly installed device (such as a modem or ONT) a new
                            DHCP address when you hot swap it. That is, when the system detects
                            a DHCP discover from a MAC address different than the one in the
                            association table, it releases the old MAC address and immediately
                            assigns an address to the new device.
                            This behavior takes effect per VLAN per port. If there is more than one
                            service on the same port sharing the same VLAN, they must use the
                            same DHCP hot swap configuration (either all enabled or disabled).
                            Note: The DHCP client must include option 61 in the DHCP packets for
                            the DHCP lease to be released from the DHCP server.
                            Note: DHCP hot swap is not supported for AE ONTs.

        :param pppoe_force_discard: expects ('true' or 'false')
                                    Discards any PPPoE frames received on an ONT port when the PPPoE
                                    profile is set in the VLAN.

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection between the client and server times-out

        :return: ont() returns a response.models.Response object on a failed call, and a nested dict on a successful call
        """
        # TODO: IMPLEMENT PARAMETER CHECKING, MAKE SURE THE EXPECTED VALUES ARE PROVIDED
        if mcast_prof_id == "0":
            _mcast_prof = """<mcast-prof></mcast-prof>"""
        else:
            _mcast_prof = f"""<mcast-prof>
                                 <type>McastProf</type>
                                 <id>
                                 <mcastprof>{mcast_prof_id}</mcastprof>
                                 </id>
                             </mcast-prof>"""

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                                <soapenv:Body>
                                    <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                        <edit-config>
                                            <target>
                                                <running/>
                                            </target>
                                            <config>
                                                <top>
                                                    <object operation="create" get-config="true">
                                                        <type>EthSvc</type>
                                                            <id>
                                                                <ont>{ont_id}</ont>
                                                                <ontslot>{ontslot}</ontslot>
                                                                <ontethany>{ontethany}</ontethany>
                                                                <ethsvc>{ethsvc}</ethsvc>
                                                            </id>
                                                            <admin>{admin_state}</admin>
                                                            <descr>{descr}</descr>
                                                            <tag-action>
                                                                <type>SvcTagAction</type>
                                                                <id>
                                                                    <svctagaction>{svctagaction_id}</svctagaction>
                                                                </id>
                                                            </tag-action>
                                                            <bw-prof>
                                                                <type>BwProf</type>
                                                                <id>
                                                                    <bwprof>{bwprof_id}</bwprof>
                                                                </id>
                                                            </bw-prof>
                                                            <out-tag>{out_tag_id}</out-tag>
                                                            <in-tag>{inner_tag_id}</in-tag>
                                                            {_mcast_prof}
                                                            <pon-cos>{pon_cos_id}</pon-cos>
                                                            <us-cir-override>{us_cir_override}</us-cir-override>
                                                            <us-pir-override>{us_pir_override}</us-pir-override>
                                                            <ds-pir-override>{ds_pir_override}</ds-pir-override>
                                                            <hot-swap>{hot_swap}</hot-swap>
                                                            <pppoe-force-discard>{pppoe_force_discard}</pppoe-force-discard>
                                                    </object>
                                                </top>
                                            </config>
                                        </edit-config>
                                    </rpc>
                                </soapenv:Body>
                            </soapenv:Envelope>"""

        if "https" not in self.client_object.cms_netconf_url:
            try:
                response = requests.post(
                    url=self.client_object.cms_netconf_url,
                    headers=self.headers,
                    data=payload,
                    timeout=self.http_timeout,
                )
            except requests.exceptions.Timeout as e:
                raise e
        else:
            # TODO: will need to research how to implement https connection with request library
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response object is returned.
            return response

        else:
            resp_dict = xmltodict.parse(response.content)
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object"
            ):
                return resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"]["top"][
                    "object"
                ]
            else:
                return response
