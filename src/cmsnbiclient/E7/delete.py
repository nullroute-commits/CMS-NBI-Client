# IMPORT STATEMENTS
import random
import requests
import xmltodict

# Additional imports if needed  
# import pydash  # Note: pydash is not in dependencies
from ..client import Client  # Import Client from relative path to avoid circular import

# IMPORT STATEMENTS


class Delete:
    def __init__(self, client_object: Client, network_nm: str = "", http_timeout: int = 1):
        """
        Description
        -----------
        Class (Delete) is the delete query constructor/posting class for the E7 CMS NETCONF NBI

        Attributes
        ----------
        :param network_nm: this parameter contains the node name, which is made of the case-sensitive name of the E7 OS platform, preceded by NTWK-. Example: NTWK-Pet02E7. The nodename value can consist of alphanumeric, underscore, and space characters, this is described in pg.26 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type network_nm:str

        :param http_timeout: this parameter is fed to the request.request() function as a timeout more can be read at the request library docs
        :type http_timeout:int

        :var self.message_id: a positive int up to 32bit is generated with each call of self.message_id, the CMS server uses this str to match requests/responses, for more infomation please read pg.29 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type self.message_id:str

        :var self.client_object: accepts object created by the cms_nbi_client.client.Client()
        :type self.client_object: object

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
                f"""Delete accepts a instance of cmsnbiclient.client.Client() or CMSClient, a instance of {type(client_object)}"""
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
        # test if the session_id is a str object
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
            "User-Agent": f"CMS_NBI_CONNECT-{self.cms_user_nm}",
        }

    @property
    def cms_user_nm(self):
        return self.client_object.cms_user_nm

    def ont(self, ont_id="", force="false"):
        """
        Description
        -----------
        function ont() performs a http/xml creation query for the provided network_nm(e7_node) requesting an <Ont> object be deleted with the provided details

        Attributes
        ----------
        :param ont_id: Identifies the ONT by its E7 scope ID (1 to 64000000), as described in pg.129 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type ont_id:str

        :param force: force expects a boolean string ['true', 'false'] Note: For a non-force(ie..force='false') delete to be successful, all service must be removed from the ONT. force="true"—Perform a force delete (deletes that all services on the ONT). as described in pg.47 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type force:str

        :raise:
            AttributeError: will be raised if the ont_id is not a digit in the form of a str object
            ConnectTimeout: will be raised if http(s) connection times out

        :return: ont() returns a response.models.Response object on a failed call, and a nested dict on a successful call
        """
        if isinstance(ont_id, str):
            if ont_id.isdigit():
                pass
            else:
                raise AttributeError(
                    """param:ont_id is expected to be a digit in the form of a str object"""
                )
        else:
            raise AttributeError(
                """param:ont_id is expected to be a digit in the form of a str object"""
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
                                            <object operation="delete" force="{force}">
                                                <type>Ont</type>
                                                <id>
                                                    <ont>{ont_id}</ont>
                                                </id>
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
            if pydash.objects.has(resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.ok"):
                return resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]
            else:
                return response

    def vlan(self, vlan_id="", force="false"):
        """
        Description
        -----------
        function vlan() performs a http/xml Deletion query for the provided network_nm(e7_node) requesting an <Vlan> object be deleted with the provided details

        Attributes
        ----------
        :param vlan_id: Identifies the VLAN: 2 to 4093 (Except for 1002-1005 which are reserved for E7 operation.), excluding any reserved VLANs as described in pg.50 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type vlan_id:str

        :param force: force expects a boolean string ['true', 'false'] Note: For a non-force(ie..force='false') delete to be successful, all membership must be removed from the vlan. force="true"—Perform a force delete (deletes that all memberships on the VLAN). as described in pg.47 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type force:str

        :raise:
            AttributeError: will be raised if the vlan_id is not a digit in the form of a str object
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: ont() returns a response.models.Response object on a failed call, and a nested dict on a successful call
        """
        if isinstance(vlan_id, str):
            if vlan_id.isdigit():
                pass
            else:
                raise AttributeError(
                    """param:vlan_id is expected to be a digit in the form of a str object"""
                )
        else:
            raise AttributeError(
                """param:vlan_id is expected to be a digit in the form of a str object"""
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
                                                    <object operation="delete" force="{force}">
                                                        <type>Vlan</type>
                                                        <id>
                                                            <vlan>{vlan_id}</vlan>
                                                        </id>
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
            if pydash.objects.has(resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.ok"):
                return resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]
            else:
                return response

    def vlanmem(self, vlan_id: str = "", vlan_member_id: str = "", force: str = "false"):
        """
        Description
        -----------
        function vlan_members() performs a http/xml creation query for the provided network_nm(e7_node) requesting an <VlanMem> object be created with the provided details

        Attributes
        ----------
        :param vlan_id:  Identifies the VLAN: 2 to 4093 (Except for 1002-1005 which are reserved for E7 operation.), excluding any reserved VLANs as described in pg.50 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type vlan_id:str

        :param vlan_member_id: —Identifies the VLAN member. 1 to 1000 as described in pg.50 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type vlan_member_id:str

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: vlan_members() will return a dict on a successful query and a response.models.response object on a failed query

        Example
        -----------

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
                                            <object operation="delete" force="{force}">
                                                <type>VlanMem</type>
                                                <id>
                                                    <vlan>{vlan_id}</vlan>
                                                    <vlanmem>{vlan_member_id}</vlanmem>
                                                </id>
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
            if pydash.objects.has(resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.ok"):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]
                return resp_dict
            else:
                return response

    def ont_ethsvc(
        self, ont_id: str = "", ontslot: str = "3", ontethany: str = "1", ethsvc: str = "1"
    ):
        """
        Description
        -----------
        function ethsvc_ont() performs a http/xml deletion query for the provided network_nm(e7_node) requesting an <ethsvc> object be deleted with the provided details

        Attributes
        ----------
        :param ont_id: Identifies the ONT by its E7 scope ID (1 to 64000000).

        :param ontslot: Identifies the ONT port type using one of the following {"Gigabit Ethernet port ": "3", "HPNA Ethernet port": "4", "Fast Ethernet port": "5" }

        :param ontethany: Identifies the ONT port number (1 to 8).

        :param ethsvc: Identifies the data service (1 to 12; typically 1 to 8 for data service).

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection between the client and server times-out

        :return: ont() returns a response.models.Response object on a failed call, and a nested dict on a successful call
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
                                                    <object operation="delete">
                                                        <type>EthSvc</type>
                                                        <id>
                                                            <ont>{ont_id}</ont>
                                                            <ontslot>{ontslot}</ontslot>
                                                            <ontethany>{ontethany}</ontethany>
                                                            <ethsvc>{ethsvc}</ethsvc>
                                                        </id>
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
            if pydash.objects.has(resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.ok"):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]
                return resp_dict
            else:
                return response
