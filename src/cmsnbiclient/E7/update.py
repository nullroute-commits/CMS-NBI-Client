# IMPORT STATEMENTS
import random

import pydash
import requests
import xmltodict

from ..client import Client  # Import Client from relative path to avoid circular import

# IMPORT STATEMENTS


class Update:
    def __init__(self, client_object: Client, network_nm: str = "", http_timeout: int = 1):
        """
        Description
        -----------
        Class (Update) is the update/merge query constructor/posting class for the E7 CMS NETCONF NBI

        Attributes
        ----------
        :param client_object:accepts object created by the cms_nbi_client.client.Client()

        :param network_nm:this parameter contains the node name, which is made of the case-sensitive name of the E7 OS platform, preceded by NTWK-. Example: NTWK-Pet02E7. The nodename value can consist of alphanumeric, underscore, and space characters, this is described in pg.26 of Calix Management System (CMS) R15.x Northbound Interface API Guide

        :param http_timeout:this parameter is fed to the request.request() function as a timeout more can be read at the request library docs

        :var self.message_id:a positive int up to 32bit is generated with each call of self.message_id, the CMS server uses this str to match requests/responses, for more infomation please read pg.29 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type self.message_id:str

        :var self.client_object:accepts object created by the cmsnbiclient.client.Client()

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
                f"""Update() accepts a instance of cmsnbiclient.client.Client() or CMSClient, a instance of {type(client_object)} was passed instead"""
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
        return {
            "Content-Type": "text/xml;charset=ISO-8859-1",
            "User-Agent": f"CMSNBICLIENT-{self.cms_user_nm}",
        }

    @property
    def cms_user_nm(self):
        return self.client_object.cms_user_nm

    def ont(
        self,
        ont_id: str = "",
        admin_state: str = "",
        ont_sn: str = "",
        reg_id: str = "",
        sub_id: str = "",
        ont_desc: str = "",
        ontpwe3prof_id: str = "",
        ontprof_id: str = "",
        us_sdber_rate: str = "",
        low_rx_opt_pwr_ne_thresh: str = "",
        high_rx_opt_pwr_ne_thresh: str = "",
        battery_present: str = "",
        pse_max_power_budget: str = "",
        poe_class_control: str = "",
        replace_sn: str = "0",
    ):
        """
        Description
        -----------
        function ont() performs a http/xml Update query for the provided network_nm(e7_node) requesting an <Ont> object be updated with the provided details

        Attributes
        ----------
        :param ont_id: Identifies the ONT by its E7 scope ID (1 to 64000000)

        :param admin_state: operational status of the created ONT, valid values are [disabled,enabled,enabled-no-alarms], this is explained further in pg.237 of Calix Management System (CMS) R15.x Northbound Interface API Guide

        :param ont_sn: identifies the Hexadecimal representation of the ONT serial number, to assign the SN at a later date, input '0', as described in pg.140 of Calix Management System (CMS) R15.x Northbound Interface API Guide

        :param reg_id: ONT registration ID that is the RONTA identifier., as described in pg.232 of Calix Management System (CMS) R15.x Northbound Interface API Guide

        :param sub_id: Identifies the subscriber ID., as described in pg.63 of Calix Management System (CMS) R15.x Northbound Interface API Guide

        :param ont_desc: Identifies the ONT Description

        :param ontpwe3prof_id: identifies the ID of the profile that sets the ONT PWE3 mode. Use 1 (also the default, if not supplied) for the system-default profile, which is set to use either T1 or E1 mode in the management interface. as described in pg.141 of Calix Management System (CMS) R15.x Northbound Interface API Guide

        :param ontprof_id: identifies the ID of a global or local ONT profile (1 to 50, or one of the default global profiles listed in Global ONT Profile IDs, as described in pg.282-285 of Calix Management System (CMS) R15.x Northbound Interface API Guide

        :param us_sdber_rate: Also Known as (Upstream Signal Degraded Error Rate) identifies the threshold for upstream bit errors before an alarm is raised range (2-6), please see pg.31 of E-Series EXA R3.x Maintenance and Troubleshooting Guide for more information

        :param low_rx_opt_pwr_ne_thresh: Also known as (Low Receive Optical Power Near End Threshold) identifies the lowest optical signal level that the ONT will accept before raising a low-rx-opt-pwr-ne alarm, default value(-30.0) accepts(-30.0 to -7.0), please see pg.61 & pg.421 of E-Series EXA R3.x Maintenance and Troubleshooting Guide for more information

        :param high_rx_opt_pwr_ne_thresh: Also known as (High Receive Optical Power Near End Threshold) identifies the highest optical signal level that the ONT will accept before raising a high-rx-opt-pwr-ne alarm, default value(-7.0) accepts(-30.0 to -7.0) please see pg.61 & pg.421 of E-Series EXA R3.x Maintenance and Troubleshooting Guide for more information

        :param battery_present: Identifies the requested batter-present state ie(true or false), this will determine if the ont alarms once it identifies the commercial power has been cut, please see pg.532 of Calix E-Series (E7 OS R3.1/R3.2) Engineering and Planning Guide for more information

        :param pse_max_power_budget: This defines the Power Sourcing Equipment (PSE) maximum power budget in Watts that the OLT can source on all Power over Ethernet (PoE) enabled Ethernet UNI ports. The PSE maximum power budget is effective in ONT only if the ownership is OMCI. default value(30) accepts(1 to 90), please see  E7 EXA R3.x GPON Applications Guide for more information

        :param poe_class_control: the port can be classified to the type of Powered Device (PD) that will be connected to the port. Different classes of PD require different amounts of power, accepts 'enabled' or 'disabled', please see pg.532 of Calix E-Series (E7 OS R3.1/R3.2) Engineering and Planning Guide for more information

        :param replace_sn: '0' or '1', this option indicates if the ont's CXNK serial number is being replaced. ont_sn must be set to '0'

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection times-out
            ValueError: Will be raised if the ont_id is not an int str ie whole number

        :return: ont() returns a response.models.Response object on a failed call, and a nested dict on a successful call

        Example
        ______

        Next we create a cmsnbiclient.E7.Update() instance and pass the cms_nbi_client.Client() instance to it
        netconf_update = cmsnbiclient.E7.Update(client, network_nm='NTWK-Example_Network, http_timeout=5)
        Once the netconf_update object is created we can then call the ont() function and update ont variables for a specific ont
        For any updated query an ont_id must be provided in the ont_id var
        Only the var(s) being updated need to be supplied

        Updating the ont 1 admin_state>>disabled
        netconf_update.ont(ont_id='1',
                           admin_state='disabled')

        Updating the ont 2 Subscriber Id  && Description
        netconf_update.ont(ont_id='2',
                           sub_id='9999999',
                           ont_desc='example_ont')

        Updating ont 4 to False on the battery_present
        netconf_update.ont(ont_id='4',
                           battery_present='false')

        Replace an ONT with a new ont
        this requires two calls one to unlink the cxnk and another to link a new cxnk
        netconf_update.ont(ont_id='4',
                           ont_sn='0',
                           replace_sn='1')

        netconf_update.ont(ont_id='4',
                           ont_sn='9999')
        """
        # using change_var as a tmp list to filter out any ont vars that are not being changed, ie the empty vars will be removed from the dictionary
        # before using xmltodict.unparse to convert it to a xml str
        par_inputs = vars()

        if isinstance(par_inputs["ont_id"], str):
            if par_inputs["ont_id"].isdigit and not par_inputs["ont_id"] == "0":
                pass
            else:
                raise ValueError(
                    f"""{par_inputs['ont_id']} NEEDS TO BE A INT STR BETWEEN 1 and 64000000"""
                )
        # APPLYING STRUCTURE TO THE PROVIDED PARAMETERS BEFORE PARSING, THIS IS DESIGN SO XMLTODICT CAN UNPARSE THE DICT INTO THE CORRECT XML FORMAT
        change_var = {
            "admin": par_inputs["admin_state"],
            "battery-present": par_inputs["battery_present"],
            "descr": par_inputs["ont_desc"],
            "high-rx-opt-pwr-ne-thresh": par_inputs["high_rx_opt_pwr_ne_thresh"],
            "low-rx-opt-pwr-ne-thresh": par_inputs["low_rx_opt_pwr_ne_thresh"],
            "ontprof": {"id": {"ontprof": par_inputs["ontprof_id"]}, "type": "OntProf"},
            "poe-class-control": par_inputs["poe_class_control"],
            "pse-max-power-budget": par_inputs["pse_max_power_budget"],
            "pwe3prof": {
                "id": {"ontpwe3prof": par_inputs["ontpwe3prof_id"]},
                "type": "OntPwe3Prof",
            },
            "reg-id": par_inputs["reg_id"],
            "serno": par_inputs["ont_sn"],
            "subscr-id": par_inputs["sub_id"],
            "us-sdber-rate": par_inputs["us_sdber_rate"],
            "linked-pon": par_inputs["replace_sn"],
        }
        # REMOVING ANY Key/Value pair that contains an empty value
        change_var = dict([(vkey, vdata) for vkey, vdata in change_var.items() if (vdata)])
        # REMOVING ANY KEY/VALUE pairs where the lowest value is empty
        # FOR link-pon it sets it to None if the value is 1(True)
        if not change_var["ontprof"]["id"]["ontprof"]:
            change_var.pop("ontprof")
        if not change_var["pwe3prof"]["id"]["ontpwe3prof"]:
            change_var.pop("pwe3prof")
        if change_var["linked-pon"] == "1":
            change_var["linked-pon"] = None
        else:
            change_var.pop("linked-pon")

        chang_xml = xmltodict.unparse(change_var, full_document=False)
        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <edit-config>
                                <target>
                                <running/>
                                </target>
                                    <config>
                                        <top>
                                            <object operation="merge" get-config="true">
                                                <type>Ont</type>
                                                <id>
                                                    <ont>{ont_id}</ont>
                                                </id>{chang_xml}
                                            </object>
                                        </top>
                                    </config>
                                </edit-config>
                            </rpc>
                            </soapenv:Body>
                        </soapenv:Envelope>"""
        # TODO: Extract UPDATE HTTP(S) Calls into Class function or property
        if "https" not in self.client_object.cms_netconf_url[:5]:
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
            # TODO:Need to implement HTTPS handling as the destination port will be different than the http port
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.Models.response object is returned.
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

    def ont_geth(
        self,
        ont_id: str = "",
        ontslot: str = "",
        ontethge: str = "",
        admin_state: str = "",
        subscr_id: str = "",
        descr: str = "",
        ontethportgos: str = "",
        duplex: str = "",
        ethsecprof: str = "",
        disable_on_batt: str = "",
        link_oam_events: str = "",
        accept_link_oam_loopbacks: str = "",
        dhcp_limit_override: str = "",
        force_dot1x: str = "",
        role: str = "",
        dscpmap: str = "",
        speed: str = "",
        poe_power_priority: str = "",
        poe_class_control: str = "",
        voice_policy_profile: str = "",
        ppte_power_control: str = "",
        policing: str = "",
    ):
        """
        Description
        -----------
        function ont_geth() performs a http/xml  query for the provided network_nm(e7_node) requesting the current data for the specified ontethge

        Attributes
        ----------
        :param ont_id: Identifies the ONT by its E7 scope ID (1 to 64000000).

        :param ontethge: Identifies the ONT-GE port number (1 to 8).

        :param admin_state: Administrative state of the ONT-GE port, valid values are [disabled,enabled,enabled-no-alarms]

        :param subscr_id: Identifies the char(32) string identifying the subscriber

        :param descr: Identifies the char(48) string identifying the port description

        :param ontethportgos: A numeric index value uniquely identifying the Ethernet GoS profile [1-10].
                              Grade-of-Service (GOS) profiles that specify reporting
                              thresholds for certain monitored attributes. For example, any time a particular count exceeds
                              a specified threshold within a certain period (either a 15-minute or one-day period), a
                              threshold-crossing alert is generated.

        :param duplex: Duplex mode for an Ethernet port [Full, Half]

        :param ethsecprof: Identifies the global Ethernet Security profile ID (1 to 16).
                           Note: The E7 implementation of security profiles applies to non-TLAN services only. For
                           TLAN services, the L2CP Filter parameter must be set to all-tunnel

        :param disable_on_batt:Identifies the port operational state when the ONT is operating on battery backup power: ['true' or 'false']

        :param link_oam_events: Identifies whether to enable OAM event monitoring: ['true' or 'false']

        :param accept_link_oam_loopbacks:Identifies whether the port accepts or rejects 802.3ah frames sent by the host: ['true' or 'false']

        :param dhcp_limit_override: To allow an override of the DHCP Lease Limit specified in a security profile
                                    applied to a port. This allows the same security profile to be reused and also
                                    allows the required DOCSIS provisioning where the lease limit is specified
                                    individually on the port on which the new service will be added.
                                    ['none','0-255']

        :param force_dot1x: An 802.1x supplicant attribute to force the supplicant to be unauthorized or
                            authorized until the force attribute is set to none.
                            ['none', 'true', 'false']

        :param role:    Expects ['uni' or 'inni']
                        For TR-167 devices where the ONU UNI port is a single UNI port attached to a
                        trusted device. Role change requires that you delete and recreate any services
                        provisioned on the port.
                        uni - the ONT port will be facing untrusted subscriber equipment (for example
                        RG, PC, STB).
                        inni - the ONT port will be facing G.fast nodes where the following behavior
                        occurs:
                         Provisioning of the MVR VLAN on the INNI port is allowed. IGMP is carried
                        upstream on their own unicast gemport/VLAN used for multicast flows.
                         When a packet contains option 82, it is passed through intact.
                        Note: The inni role only applies to ONT Gigabit Ethernet ports, ONT Fast
                        Ethernet ports, and ONT HPNA Ethernet ports. This attribute can be changed
                        only when there is no Ethernet service currently provisioned on the port. Only
                        one single video VLAN per INNI port is supported. One PPPoE session per
                        G.fast node port. Four DHCP sessions per G.fast node port

        :param dscpmap:  identifies the global DSCP Map profile ID (1 to 10).

        :param speed: Expects ['auto', '1000'] Identifies the data rate of the Ethernet port, setting to 1000 will disable auto negotiation

        :param poe_power_priority:  The ports can be prioritized ['low', 'medium', 'high'] for Power over Ethernet (PoE).
                                    If there is not enough power available to source all ports, the ONT drops the
                                    lower priority ports first.

        :param poe_class_control:   Expects ['enabled' or 'disabled']
                                    The port can be classified to the type of Powered Device (PD) that will be
                                    connected to the port. Different classes of PD require different amounts of
                                    power.

        :param voice_policy_profile: TODO: Research correct voice policy method as im not finding anything online for the correct formating

        :param ppte_power_control:  Expects ['true', 'false']
                                    Enables or disables Power over Ethernet (PoE) on the port.
                                    GPON will implicitly enable Link Layer Discovery Protocol (LLDP) on the ONT
                                    when either PoE is enabled or when the Voice Policy is defined.


        :param policing: expects ['enable', 'disable']
                        Ingress rate limiting is sometimes called traffic policing because it ensures ingress traffic
                        does not exceed a specified bit rate, keeping a subscriber from exceeding their data rate
                        contract. Rate limiting applies to traffic entering an E-Series network from a downstream
                        device

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection between the client and server times-out

        :return: ont() returns a response.models.Response object on a failed call, and a nested dict on a successful call
        """

        # using change_var as a tmp list to filter out any ont vars that are not being changed, ie the empty vars will be removed from the dictionary
        # before using xmltodict.unparse to convert it to a xml str
        par_inputs = vars()

        if isinstance(par_inputs["ont_id"], str):
            if par_inputs["ont_id"].isdigit and not par_inputs["ont_id"] == "0":
                pass
            else:
                raise ValueError(
                    f"""{par_inputs['ont_id']} NEEDS TO BE A INT STR BETWEEN 1 and 64000000"""
                )
        # APPLYING STRUCTURE TO THE PROVIDED PARAMETERS BEFORE PARSING, THIS IS DESIGN SO XMLTODICT CAN UNPARSE THE DICT INTO THE CORRECT XML FORMAT
        change_var = {
            "accept-link-oam-loopbacks": par_inputs["accept_link_oam_loopbacks"],
            "admin": par_inputs["admin_state"],
            "descr": par_inputs["descr"],
            "dhcp-limit-override": par_inputs["dhcp_limit_override"],
            "disable-on-batt": par_inputs["disable_on_batt"],
            "duplex": par_inputs["duplex"],
            "force-dot1x": par_inputs["force_dot1x"],
            "gos": {"id": {"ontethportgos": par_inputs["ontethportgos"]}, "type": "OntEthPortGos"},
            "link-oam-events": par_inputs["link_oam_events"],
            "pbit-map": {"id": {"dscpmap": par_inputs["dscpmap"]}, "type": "DscpMap"},
            "poe-class-control": par_inputs["poe_class_control"],
            "poe-power-priority": par_inputs["poe_power_priority"],
            "policing": par_inputs["policing"],
            "ppte-power-control": par_inputs["ppte_power_control"],
            "role": par_inputs["role"],
            "sec": {"id": {"ethsecprof": par_inputs["ethsecprof"]}, "type": "EthSecProf"},
            "speed": par_inputs["speed"],
            "subscr-id": par_inputs["subscr-id"],
        }
        # TODO: Research correct voice policy method as im not finding anything online for the correct formating
        # REMOVING ANY SINGLE LEVEL KEY/VALUE pairs where the lowest value is empty
        change_var = dict([(vkey, vdata) for vkey, vdata in change_var.items() if (vdata)])
        # REMOVING ANY SINGLE LEVEL KEY/VALUE pairs where the lowest value is empty

        # REMOVING THE REMAINING EMPTY MULTILEVEL DICTIONARY
        if not pydash.objects.get("gos.id.ontethportgos", change_var):
            change_var.pop("gos")
        if not pydash.objects.get("pbit-map.id.dscpmap", change_var):
            change_var.pop("pbit-map")
        if not pydash.objects.get("sec.id.ethsecprof", change_var):
            change_var.pop("sec")
        # REMOVING THE REMAINING EMPTY MULTILEVEL DICTIONARY

        chang_xml = xmltodict.unparse(change_var, full_document=False)

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                                <soapenv:Body>
                                    <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                        <edit-config>
                                            <target>
                                                <running/>
                                            </target>
                                            <config>
                                                <top>
                                                    <object operation="merge">
                                                        <type>OntEthGe</type>
                                                        <id>
                                                            <ont>{ont_id}</ont>
                                                            <ontslot>{ontslot}</ontslot>
                                                            <ontethge>{ontethge}</ontethge>
                                                        </id>
                                                        {chang_xml}
                                                    </object>
                                                </top>
                                            </config>
                                        </edit-config>
                                    </rpc>
                                    </soapenv:Body>
                                </soapenv:Envelope>"""
        # TODO: Extract UPDATE HTTP(S) Calls into Class function or property
        if "https" not in self.client_object.cms_netconf_url[:5]:
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
            # TODO:Need to implement HTTPS handling as the destination port will be different than the http port
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.Models.response object is returned.
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

    def ont_ethsvc(
        self,
        ont_id: str = "",
        ontslot: str = "",
        ontethany: str = "",
        ethsvc: str = "",
        admin_state: str = "",
        descr: str = "",
        svctagaction_id: str = "",
        bwprof_id: str = "",
        out_tag: str = "",
        inner_tag: str = "",
        mcast_prof_id: str = "",
        pon_cos: str = "",
        us_cir_override: str = "",
        us_pir_override: str = "",
        ds_pir_override: str = "",
        hot_swap: str = "",
        pppoe_force_discard: str = "",
    ):
        """
        Description
        -----------
        function ethsvc_ont() performs a http/xml update query for the provided network_nm(e7_node) requesting an <ethsvc> object be created with the provided details

        Attributes
        ----------
        :param ont_id: Identifies the ONT by its E7 scope ID (1 to 64000000).

        :param ontslot: Identifies the ONT port type using one of the following {"Gigabit Ethernet port ": "3", "HPNA Ethernet port": "4", "Fast Ethernet port": "5" }

        :param ontethany: Identifies the ONT port number (1 to 8).

        :param ethsvc: Identifies the data service (1 to 12; typically 1 to 8 for data service).

        :param admin_state: Administrative status of the targeted ONT port (disabled, enabled, enabled-no-alarms).

        :param descr: Description of service.

        :param svctagaction_id: Identifies the ID of a predefined global service tag action (1 to 255).

        :param bwprof_id: Identifies the ID of a global or local Ethernet bandwidth profile (1 to 300).
                          The CMS XML NBI may be used to provision services using local profile IDs.
                          Previously, the CMS XML NBI accepted only global profile IDs.
                          The local ID is specified using the syntax "local:X" where "X" is the local profile ID number.

        :param out_tag_id: "outer"(S-TAG) QinQ(802.1ad) VLAN IDs (2 to 4093, excluding any reserved VLAN IDs). Except for 1002-1005 which are reserved for E7 operation.

        :param inner_tag_id: "inner"(C-TAG) Dot1q(802.1Q) VLAN IDs (2 to 4093, excluding any reserved VLAN IDs). Except for 1002-1005 which are reserved for E7 operation.

        :param mcast_prof_id: Identifies an ID of a pre-defined global or local multicast profile (1 to 32).
                              The CMS XML NBI may be used to provision services using local profile IDs.
                              Previously, the CMS XML NBI accepted only global profile IDs.
                              The local ID is specified using the syntax "local:X" where "X" is the local profile ID number.

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

        :param hot_swap: accepted inputs ('true' or 'false')
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

        :param pppoe_force_discard: accepted inputs ('true' or 'false')
                                    Discards any PPPoE frames received on an ONT port when the PPPoE
                                    profile is set in the VLAN.

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection between the client and server times-out

        :return: ont_ethsvc() returns a response.models.Response object on a failed call, and a nested dict on a successful call
        """
        par_input = vars()
        # using change_var_list as a tmp list to filter out any ont vars that are not being changed, ie the empty vars will be removed from the dictionary
        # before using xmltodict.unparse to convert it to a xml str
        # APPLYING STRUCTURE TO THE PROVIDED PARAMETERS BEFORE PARSING, THIS IS DESIGN SO XMLTODICT CAN UNPARSE THEM INTO THE CORRECT XML FORMAT
        change_var = {
            "admin": par_input["admin_state"],
            "descr": par_input["descr"],
            "tag-action": {
                "type": "SvcTagAction",
                "id": {"svctagaction": par_input["svctagaction_id"]},
            },
            "bw-prof": {"type": "BwProf", "id": {"bwprof": par_input["bwprof_id"]}},
            "out-tag": par_input["out_tag"],
            "in-tag": par_input["inner_tag"],
            "mcast-prof": {"type": "McastProf", "id": {"mcastprof": par_input["mcast_prof_id"]}},
            "pon-cos": par_input["pon_cos"],
            "us-cir-override": par_input["us_cir_override"],
            "us-pir-override": par_input["us_pir_override"],
            "ds-pir-override": par_input["ds_pir_override"],
            "hot-swap": par_input["hot_swap"],
            "pppoe-force-discard": par_input["pppoe_force_discard"],
        }
        # REMOVING ANY SINGLE LEVEL KEY/VALUE pairs where the lowest value is empty
        change_var = dict([(vkey, vdata) for vkey, vdata in change_var.items() if (vdata)])
        # REMOVING ANY SINGLE LEVEL KEY/VALUE pairs where the lowest value is empty

        # REMOVING THE REMAINING EMPTY MULTILEVEL DICTIONARY
        if not pydash.objects.get("bw-prof.id.bwprof", change_var):
            change_var.pop("bw-prof")
        if not pydash.objects.get("tag-action.id.svctagaction", change_var):
            change_var.pop("tag-action")
        if not pydash.objects.get("mcast-prof.id.mcastprof", change_var):
            change_var.pop("mcast-prof")
        # REMOVING THE REMAINING EMPTY MULTILEVEL DICTIONARY

        chang_xml = xmltodict.unparse(change_var, full_document=False)
        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                                        <soapenv:Body>
                                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                                <edit-config>
                                                    <target>
                                                        <running/>
                                                    </target>
                                                    <config>
                                                        <top>
                                                            <object operation="merge">
                                                                <type>EthSvc</type>
                                                                <id>
                                                                    <ont>{ont_id}</ont>
                                                                    <ontslot>{ontslot}</ontslot>
                                                                    <ontethany>{ontethany}</ontethany>
                                                                    <ethsvc>{ethsvc}</ethsvc>
                                                                </id>
                                                                {chang_xml}
                                                            </object>
                                                        </top>
                                                    </config>
                                                </edit-config>
                                            </rpc>
                                            </soapenv:Body>
                                        </soapenv:Envelope>"""

        # TODO: Extract UPDATE HTTP(S) Calls into Class function or property
        if "https" not in self.client_object.cms_netconf_url[:5]:
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
            # TODO:Need to implement HTTPS handling as the destination port will be different than the http port
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.Models.response object is returned.
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
