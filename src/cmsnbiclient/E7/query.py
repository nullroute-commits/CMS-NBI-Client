# IMPORT STATEMENTS
import random
from typing import Any

import pydash
import requests
import xmltodict

from ..client import Client  # Import Client from relative path to avoid circular import

# IMPORT STATEMENTS


class Query:
    def __init__(self, client_object: Client, network_nm: str = "", http_timeout: int = 1):
        """
        Description
        -----------
        Class (Query) is the query constructor/posting class for the E7 CMS NETCONF NBI

        Attributes
        ----------
        :param client_object: accepts object created by the cms_nbi_client.client.Client()
        :type client_object:Client

        :param network_nm: this parameter contains the node name, which is made of the case-sensitive name of the E7 OS platform, preceded by NTWK-. Example: NTWK-Pet02E7. The nodename value can consist of alphanumeric, underscore, and space characters, this is described in pg.26 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type network_nm:str

        :param http_timeout: this parameter is fed to the request.request() function as a timeout more can be read at the request library docs
        :type http_timeout:int

        :var self.message_id: a positive int up to 32bit is generated with each call of self.message_id, the CMS server uses this str to match requests/responses, for more infomation please read pg.29 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type self.message_id:str

        :var self.client_object: accepts object created by the cmsnbiclient.client.Client()
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
                f"""Query_E7_Data accepts a instance of Client or CMSClient, a instance of {type(client_object)}"""
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
            raise ValueError("self.client_object.cms_netconf_url must be a str object")
        # TEST THE SESSION_ID VAR, THIS INSURES THAT ANY REQUEST ARE GOOD TO AUTHED
        if isinstance(self.client_object.session_id, str):
            if self.client_object.session_id.isdigit():
                pass
            else:
                raise ValueError("self.client_object.session_id must be a int in a str object")
        else:
            raise ValueError("self.client_object.session_id must be a str object")
        # TEST IF THE NETWORK_NM is an empty string
        if isinstance(network_nm, str):
            if len(network_nm) >= 1:
                pass
            else:
                raise ValueError("network_nm cannot be an empty str")
        else:
            raise ValueError("network_nm must be a str")
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

    def system(self):
        """
        Description
        -----------
        function system() performs a http/xml query to the provided network_nm(e7_node) requesting the <system> object type

        Attributes
        ----------

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: system() will return a nested dict on a successful call and a requests.models.Response object on a failed call
        """

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                            <soapenv:Body>
                                <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                    <get>
                                        <filter type="subtree">
                                            <top>
                                                <object>
                                                    <type>System</type><id/>
                                                </object>
                                            </top>
                                        </filter>
                                    </get>
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
            # TODO: IMPLEMENT HTTPS HANDLING
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

    def system_children(self, after_filter={"": ""}) -> Any:
        """
        Description
        -----------
        function system_children() performs a http/xml query for the provided network_nm(e7_node) requesting the children of the <system> object type

        Attributes
        ----------
        :param after_filter: this parameter is a dict of the child object to input in the <after> element as shown in pg.18 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type after_filter:dict

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: system_children() returns a requests.models.Response object on a failed call, and a nested dict on a successful call
        """
        if "type" in after_filter.keys():
            _after = f"""\n<after>\n<type>{after_filter['type']}</type>\n<id>\n<{after_filter['type'].lower()}>{after_filter['id']}<{'/' + after_filter['type'].lower()}>\n</id>\n</after>\n"""
        else:
            _after = ""

        payload = f"""
        <soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
        <soapenv:Body>
        <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
        <get-config>
        <source>
        <running/>
        </source>
        <filter type="subtree">
        <top>
        <object>
        <type>System</type>
        <id></id>
        <children>{_after}</children>
        </object>
        </top>
        </filter>
        </get-config>
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
            # TODO: IMPLEMENT HTTPS HANDLING
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response is returned.
            return response

        else:
            # The response code is NOT 200, the xmltodict.parse method is called to convert the xml respose to a dictionary.
            resp_dict = xmltodict.parse(response.content)
            # the pydash.object.has method is called to test if the path provided exist,
            # in this case its looking for 'more' as being apart of the path, this indicated there are more children to query
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.more"
            ):
                # set the local variable resp_dict to just the data contained in the child xml tag
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]["children"]["child"]
                # this portion of the if statement parses the last value in the dictionary and extracts the <type> and <id> tag values
                last_object_type = [x for x in resp_dict[len(resp_dict) - 1].items()]
                id_key = [key for key in last_object_type[1][1].keys()][0]
                _after_filter_ = {}
                _after_filter_["type"] = last_object_type[0][1]
                _after_filter_["id"] = pydash.get(last_object_type[1][1][id_key], "#text")
                # this portion of the if statement parses the last value in the dictionary and extracts the <type> and <id> tag values
                # this try/except clause test the objectresp_system_childrenvariable, if it doesnt exist it is created and updated
                try:
                    if isinstance(self.resp_system_children, list):
                        self.resp_system_children.extend(resp_dict)
                except AttributeError:
                    self.resp_system_children = []
                    self.resp_system_children.extend(resp_dict)
                # Recursive method for pulling the rest of the children
                return self.system_children(after_filter=_after_filter_)
            elif pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]["children"]["child"]
                try:
                    if isinstance(self.resp_system_children, list):
                        self.resp_system_children.extend(resp_dict)
                        resp_system_children = self.resp_system_children
                        del self.resp_system_children
                        return resp_system_children
                except AttributeError:
                    self.resp_system_children = []
                    self.resp_system_children.extend(resp_dict)
                    resp_system_children = self.resp_system_children
                    del self.resp_system_children
                    return resp_system_children
            else:
                return response

    def system_children_discont(self, after_filter={"": ""}, attr_filter={"": ""}) -> Any:
        """
        Description
        -----------
        function system_children_discont() performs a http/xml query for the provided network_nm(e7_node) requesting the <Discont> children of the <system> object type

        Attributes
        ----------
        :param after_filter: this parameter is a dict of the child object to input in the <after> element as shown in pg.18 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type after_filter:dict

        :param attr_filter: expects a dictionary with the attr as the key and the attr_val as the value, this is used to perform the attr-filter action as mentioned in pg.40 of the Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type attr_filter:dict

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: system_children_discont() will return a requests.models.Response object on a failed call, and a list of nested dict on a successful call
        """
        if "discont" in after_filter.keys():
            after_filter = f"""<after>
                                <type>DiscOnt</type>
                                    <id>
                                        <discont>{after_filter['discont']}</discont>
                                    </id>
                                </after>"""
        else:
            after_filter = ""

        valid_attr = [
            "op-stat",
            "crit",
            "maj",
            "min",
            "warn",
            "info",
            "derived-states",
            "reg-id",
            "prov-reg-id",
            "pon",
            "model",
            "vendor",
            "clei",
            "ont",
            "subscr-id",
            "descr",
            "curr-sw-vers",
            "alt-sw-vers",
            "curr-committed",
            "mfg-serno",
            "product-code",
            "curr-cust-vers",
            "alt-cust-vers",
            "onu-mac",
            "mta-mac",
            "link-permit-status",
        ]
        if "" not in attr_filter.keys():
            _attr_filter = """<attr-filter>"""
            for attr in attr_filter.items():
                if attr[0] in valid_attr:
                    if attr[0] == "pon":
                        _attr_filter = (
                            _attr_filter
                            + f"""<type>GponPort</type>\n<id>\n<shelf>{attr[1]['shelf']}</shelf>\n<card>{attr[1]['card']}</card>\n<gponport>{attr[1]['gponport']}</gponport>\n</id>\n"""
                        )
                    else:
                        _attr_filter = _attr_filter + f"""<{attr[0]}>{attr[1]}</{attr[0]}>\n"""
                else:
                    pass
            _attr_filter = _attr_filter + """</attr-filter>"""
        else:
            _attr_filter = """<attr-filter></attr-filter>"""

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                            <soapenv:Body>
                                <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                    <get>
                                        <filter type="subtree">
                                            <top>
                                                <object>
                                                    <type>System</type>
                                                    <id/>
                                                    <children>
                                                        <type>DiscOnt</type>
                                                        {after_filter}
                                                        {_attr_filter}
                                                        <attr-list>op-stat crit maj min warn info derived-states reg-id prov-reg-id pon model vendor clei ont ontprof subscr-id descr curr-sw-vers alt-sw-vers curr-committed mfg-serno product-code curr-cust-vers alt-cust-vers onu-mac mta-mac link-permit-status</attr-list>
                                                    </children>
                                                </object>
                                            </top>
                                        </filter>
                                    </get>
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
            # TODO: IMPLEMENT HTTPS HANDLING
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response object is returned.
            return response

        else:
            resp_dict = xmltodict.parse(response.content)
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.more"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]["children"]["child"]
                after_filter_ = resp_dict[len(resp_dict) - 1]["id"]
                try:
                    if isinstance(self.resp_system_children_discont, list):
                        self.resp_system_children_discont.extend(resp_dict)
                except AttributeError:
                    self.resp_system_children_discont = []
                    self.resp_system_children_discont.extend(resp_dict)
                return self.system_children_discont(
                    after_filter=after_filter_, attr_filter=attr_filter
                )
            elif pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]["children"]["child"]
                try:
                    if isinstance(self.resp_system_children_discont, list):
                        for resp in resp_dict:
                            self.resp_system_children_discont.append(resp)
                        resp_system_discont = self.resp_system_children_discont
                        del self.resp_system_children_discont
                        return resp_system_discont
                except:
                    self.resp_system_children_discont = []
                    self.resp_system_children_discont.append(resp_dict)
                    resp_system_discont = self.resp_system_children_discont
                    del self.resp_system_children_discont
                    return resp_system_discont

            elif pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children"
            ):
                if (
                    resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"]["top"][
                        "object"
                    ]["children"]
                    is None
                ):
                    try:
                        isinstance(self.resp_system_children_discont, list)
                        resp_system_discont = self.resp_system_children_discont
                        del self.resp_system_children_discont
                        return resp_system_discont
                    except:
                        return response

                else:
                    return response
            else:
                return response

    def system_children_ontprof(self, after_filter={"": ""}, attr_filter={"": ""}):
        """
        Description
        -----------
        function system_children_ontprof() performs a http/xml query for the provided network_nm(e7_node) requesting the <OntProf> children of the <system> object type

        Attributes
        ----------
        :param after_filter: this parameter is a dict of the child object to input in the <after> element as shown in pg.18 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type after_filter:dict

        :param attr_filter: expects a dictionary with the attr as the key and the attr_val as the value, this is used to perform the attr-filter action as mentioned in pg.40 of the Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type attr_filter:dict

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: system_children_ontprof() returns a requests.models.Response object on a failed query and a nested dict on a successful query
        """
        if "ontprof" in after_filter.keys():
            _after_filter = f"""<after>
                                <type>OntProf</type>
                                    <id>
                                        <ontprof>{after_filter['ontprof']}</ontprof>
                                    </id>
                                </after>"""
        else:
            _after_filter = """"""

        valid_attr = [
            "name",
            "vendor",
            "model",
            "pots",
            "feth",
            "geth",
            "hpnaeth",
            "ds1",
            "rfvid",
            "hotrfvid",
            "eth-oam-capable",
            "convert-mcast-capable",
            "rg",
            "fb",
            "default-to-rg",
        ]
        if "" not in attr_filter.keys():
            _attr_filter = """<attr-filter>"""
            for attr in attr_filter.items():
                if attr[0] in valid_attr:
                    _attr_filter = _attr_filter + f"""<{attr[0]}>{attr[1]}</{attr[0]}>"""
            _attr_filter = _attr_filter + """</attr-filter>"""
        else:
            _attr_filter = "<attr-filter></attr-filter>"
        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <get-config>
                                    <source>
                                        <running/>
                                    </source>
                                    <filter type="subtree">
                                        <top>
                                            <object>
                                                <type>System</type>
                                                <id/>
                                                <children>
                                                    <type>OntProf</type>
                                                    {_after_filter}
                                                    {_attr_filter}
                                                    <attr-list>name vendor model pots feth geth hpnaeth ds1 rfvid hotrfvid eth-oam-capable convert-mcast-capable rg fb default-to-rg</attr-list>
                                                </children>
                                            </object>
                                        </top>
                                    </filter>
                                </get-config>
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
            # TODO: IMPLEMENT HTTPS HANDLING
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response object is returned.
            return response

        else:
            resp_dict = xmltodict.parse(response.content)
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.more"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]["children"]["child"]
                after_filter_ = resp_dict[len(resp_dict) - 1]["id"]
                _after_filter_ = {"ontprof": f'{after_filter_["ontprof"]["#text"]}'}
                try:
                    if isinstance(self.resp_system_children_ontprof, list):
                        self.resp_system_children_ontprof.extend(resp_dict)
                except:
                    self.resp_system_children_ontprof = []
                    self.resp_system_children_ontprof.extend(resp_dict)
                return self.system_children_ontprof(
                    after_filter=_after_filter_, attr_filter=attr_filter
                )
            elif pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]["children"]["child"]
                try:
                    if isinstance(self.resp_system_children_ontprof, list):
                        if len(resp_dict) > 1:
                            self.resp_system_children_ontprof.extend(resp_dict)
                            resp_system_children_ontprof = self.resp_system_children_ontprof
                            del self.resp_system_children_ontprof
                        else:
                            self.resp_system_children_ontprof.append(resp_dict)
                            resp_system_children_ontprof = self.resp_system_children_ontprof
                            del self.resp_system_children_ontprof
                        return resp_system_children_ontprof
                except:
                    self.resp_system_children_ontprof = []
                    self.resp_system_children_ontprof.append(resp_dict)
                    resp_system_children_ontprof = self.resp_system_children_ontprof
                    del self.resp_system_children_ontprof
                    return resp_system_children_ontprof
            else:
                return response

    def system_children_ontpwe3prof(self, after_filter={"": ""}, attr_filter={"": ""}):
        """
        Description
        -----------
        function system_children_ontpwe3prof() performs a http/xml query for the provided network_nm(e7_node) requesting the <OntPwe3Prof> children of the <System> object type

        Attributes
        ----------
        :param after_filter: this parameter is a dict of the child object to input in the <after> element as shown in pg.18 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type after_filter:dict

        :param attr_filter: expects a dictionary with the attr as the key and the attr_val as the value, this is used to perform the attr-filter action as mentioned in pg.40 of the Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type attr_filter:dict

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: system_children_ontpwe3prof() returns a requests.models.Response object on a failed query and a list of nested dict on a successful query
        """
        if "" not in after_filter.keys():
            pass
        else:
            _after_filter = """"""

        valid_attr = ["name", "tdm-mode"]
        if "" not in attr_filter.keys():
            _attr_filter = """<attr-filter>"""
            for attr in attr_filter.items():
                if attr[0] in valid_attr:
                    _attr_filter = _attr_filter + f"""<{attr[0]}>{attr[1]}</{attr[0]}>"""
            _attr_filter = _attr_filter + """</attr-filter>"""
        else:
            _attr_filter = """<attr-filter></attr-filter>"""

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <get-config>
                                    <source>
                                        <running/>
                                    </source>
                                    <filter type="subtree">
                                        <top>
                                            <object>
                                                <type>System</type>
                                                <id/>
                                                <children>
                                                    <type>OntPwe3Prof</type>
                                                    {_after_filter}
                                                    {_attr_filter}
                                                    <attr-list>name tdm-mode</attr-list>
                                                </children>
                                            </object>
                                        </top>
                                    </filter>
                                </get-config>
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
            # TODO: IMPLEMENT HTTPS HANDLING
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response object is returned.
            return response

        else:
            resp_dict = xmltodict.parse(response.content)
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.more"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]["children"]["child"]
                after_filter_ = resp_dict[len(resp_dict) - 1]["id"]
                _after_filter_ = {"ontprof": f'{after_filter_["ontprof"]["#text"]}'}
                try:
                    if isinstance(self.resp_system_children_ontpwe3prof, list):
                        self.resp_system_children_ontpwe3prof.extend(resp_dict)
                except:
                    self.resp_system_children_ontpwe3prof = []
                    self.resp_system_children_ontpwe3prof.extend(resp_dict)
                return self.system_children_ontpwe3prof(
                    after_filter=_after_filter_, attr_filter=attr_filter
                )
            elif pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]["children"]["child"]
                try:
                    if isinstance(self.resp_system_children_ontpwe3prof, list):
                        if len(resp_dict) > 1:
                            self.resp_system_children_ontpwe3prof.extend(resp_dict)
                            resp_system_children_ontpwe3prof = self.resp_system_children_ontpwe3prof
                            del self.resp_system_children_ontpwe3prof
                        else:
                            self.resp_system_children_ontpwe3prof.append(resp_dict)
                            resp_system_children_ontpwe3prof = self.resp_system_children_ontpwe3prof
                            del self.resp_system_children_ontpwe3prof
                        return resp_system_children_ontpwe3prof
                except:
                    self.resp_system_children_ontpwe3prof = []
                    self.resp_system_children_ontpwe3prof.append(resp_dict)
                    resp_system_children_ontpwe3prof = self.resp_system_children_ontpwe3prof
                    del self.resp_system_children_ontpwe3prof
                    return resp_system_children_ontpwe3prof
            else:
                return response

    def system_children_vlan(self, after_filter={"": ""}, attr_filter={"": ""}):
        """
        Description
        -----------
        function system_children_vlan() performs a http/xml query for the provided network_nm(e7_node) requesting the <Vlan> children of the <System> object type

        Attributes
        ----------
        :param after_filter: this parameter is a dict of the child object to input in the <after> element as shown in pg.18 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type after_filter:dict

        :param attr_filter: expects a dictionary with the attr as the key and the attr_val as the value, this is used to perform the attr-filter action as mentioned in pg.40 of the Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type attr_filter:dict

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: system_children_vlan() returns a requests.models.Response object on a failed query and a list of nested dict on a successful query
        """
        # After Filter Parser
        if "" not in after_filter.keys():
            _after_filter = (
                f"""<after>{xmltodict.unparse(after_filter, full_document=False)}</after>"""
            )
        else:
            _after_filter = """"""

        # Attr-Filter Parser
        if "" not in attr_filter.keys():
            _attr_filter = f"""<attr-filter>{xmltodict.unparse(attr_filter, full_document=False)}</attr-filter>"""
        else:
            _attr_filter = """"""

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <get-config>
                                    <source>
                                        <running/>
                                    </source>
                                    <filter type="subtree">
                                        <top>
                                            <object>
                                                <type>System</type>
                                                <id/>
                                                <children>
                                                    <type>Vlan</type>
                                                    {_after_filter}
                                                    {_attr_filter}
                                                    <attr-list>name igmp-mode igmp-prof dhcp-mode mac-force-forw ip-src-verify mac-learn ae-ont-discovery pon-tlan pon-hairpin igmp-pbit dhcp-svc-prof option82-enable eth-opt82prof gpon-opt82prof mobility pppoe-prof</attr-list>
                                                </children>
                                            </object>
                                        </top>
                                    </filter>
                                </get-config>
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
            # TODO: IMPLEMENT HTTPS HANDLING
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response object is returned.
            return response

        else:
            resp_dict = xmltodict.parse(response.content)
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.more"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]["children"]["child"]
                last_entry = {
                    "type": "Vlan",
                    "id": {"vlan": resp_dict[len(resp_dict) - 1]["id"]["vlan"]["#text"]},
                }
                try:
                    if isinstance(self.resp_system_children_vlan, list):
                        self.resp_system_children_vlan.extend(resp_dict)
                except:
                    self.resp_system_children_vlan = []
                    self.resp_system_children_vlan.extend(resp_dict)
                return self.system_children_vlan(after_filter=last_entry, attr_filter=attr_filter)

            elif pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.child"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]["children"]["child"]
                try:
                    if isinstance(self.resp_system_children_vlan, list):
                        if isinstance(resp_dict, list):
                            self.resp_system_children_vlan.extend(resp_dict)
                        else:
                            self.resp_system_children_vlan.append(resp_dict)
                except:
                    self.resp_system_children_vlan = []
                    if isinstance(resp_dict, list):
                        self.resp_system_children_vlan.extend(resp_dict)
                    else:
                        self.resp_system_children_vlan.append(resp_dict)
                resp = self.resp_system_children_vlan
                del self.resp_system_children_vlan
                return resp
            elif pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children"
            ):
                if isinstance(self.resp_system_children_vlan, list):
                    resp = self.resp_system_children_vlan
                    del self.resp_system_children_vlan
                    return resp
                else:
                    return response
            else:
                return response

    def ont_children_ethsvc(self, ont_id="", after_filter={"": ""}, attr_filter={"": ""}):
        """
        Description
        -----------
        function ont_children_ethsvc() performs a http/xml query for the provided network_nm(e7_node) requesting the <EthSvc> children of the <ONT> object type

        Attributes
        ----------
        :param ont_id: ONT ID value
        :type: ont_id:str

        :param after_filter: this parameter is a dict of the child object to input in the <after> element as shown in pg.18 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type after_filter:dict

        :param attr_filter: expects a dictionary with the attr as the key and the attr_val as the value, this is used to perform the attr-filter action as mentioned in pg.40 of the Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type attr_filter:dict

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: ont_children_ethsvc() returns a requests.models.Response object on a failed/empty query and a list of nested dict on a successful query


        Example
        -----------
        # ALL EthSvc on the specified ONT_ID
        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1')

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
        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1',
                                          attr_filter={'admin': 'enabled'})

        # ------BY EthSvc DESCRIPTION------
        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1',
                                          attr_filter={'descr': 'example_description'})

        # ------BY SvcTagAction ID------
        # Using an SvcTagAction ID of 1
        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1',
                                          attr_filter={'tag-action':
                                                           {'type': 'SvcTagAction',
                                                            'id': {'svctagaction': '1'}}})

        # ------BY BANDWIDTH PROFILE ID------
        # Using an BwProf ID of 1
        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1',
                                          attr_filter={'bw-prof':
                                                           {'type': 'BwProf',
                                                            'id': {'bwprof': '1'}}})

        # ------BY OUTER VLAN TAG------
        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1',
                                          attr_filter={'out-tag': '2'})

        # ------BY INNER VLAN TAG------
        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1',
                                          attr_filter={'in-tag': '2'})

        # ------BY MULTICAST PROFILE ID------
        # Using an McastProf ID of 1
        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1',
                                          attr_filter={'mcast-prof': {'type': 'McastProf',
                                                                      'id': {'mcastprof': '1'}}})

        # Using an None as the Mcast value, this will search for all EthSvc with no McastProf applied
        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1',
                                          attr_filter={'mcast-prof': None})


        # ------BY PON COS------
        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1',
                                          attr_filter={'pon-cos': 'derived'})

        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1',
                                          attr_filter={'pon-cos': 'cos-1'})

        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1',
                                          attr_filter={'pon-cos': 'user-1'})

        query_e7_data.ont_children_ethsvc(message_id='1',
                                          cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                                          network_nm='NTWK-Example_Name',
                                          http_timeout=1,
                                          ont_id='1',
                                          attr_filter={'pon-cos': 'fixed'})
        """

        if "" not in after_filter.keys():
            _after_filter = (
                f"""<after>{xmltodict.unparse(after_filter, full_document=False)}</after>"""
            )
        else:
            _after_filter = """"""

        if "" not in attr_filter.keys():
            _attr_filter = f"""<attr-filter>{xmltodict.unparse(attr_filter, full_document=False)}</attr-filter>"""
        else:
            _attr_filter = """<attr-filter></attr-filter>"""

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <get-config>
                                    <source>
                                        <running/>
                                    </source>
                                    <filter type="subtree">
                                        <top>
                                            <object>
                                                <type>Ont</type>
                                                <id>
                                                    <ont>{ont_id}</ont>
                                                </id>
                                                <children>
                                                    <type>EthSvc</type>
                                                        {_after_filter}
                                                        {_attr_filter}
                                                    <attr-list>admin descr tag-action bw-prof out-tag in-tag mcast-prof pon-cos us-cir-override us-pir-override ds-pir-override hot-swap pppoe-force-discard</attr-list>
                                                </children>
                                            </object>
                                        </top>
                                    </filter>
                                </get-config>
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
            # TODO: IMPLEMENT HTTPS HANDLING
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response object is returned.
            return response

        else:
            resp_dict = xmltodict.parse(response.content)
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children.more"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]["children"]["child"]
                last_entry = resp_dict[len(resp_dict) - 1]
                __after_filter = {
                    "type": last_entry["type"],
                    "id": {
                        "ont": last_entry["id"]["ont"],
                        "ontslot": last_entry["id"]["ontslot"],
                        "ontethany": last_entry["id"]["ontethany"],
                        "ethsvc": last_entry["id"]["ethsvc"]["#text"],
                    },
                }
                try:
                    if isinstance(self.resp_ont_children_ethsvc, list):
                        self.resp_ont_children_ethsvc.extend(resp_dict)
                except:
                    self.resp_ont_children_ethsvc = []
                    self.resp_ont_children_ethsvc.extend(resp_dict)
                return self.ont_children_ethsvc(
                    ont_id=ont_id, after_filter=__after_filter, attr_filter=attr_filter
                )
            elif pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.data.top.object.children"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"]["data"][
                    "top"
                ]["object"]["children"]
                # Trying to catch NONE type objects and not append them to the list
                if not isinstance(resp_dict, type(None)):
                    try:
                        if isinstance(self.resp_ont_children_ethsvc, list):
                            if isinstance(resp_dict, list):
                                self.resp_ont_children_ethsvc.extend(resp_dict)
                            else:
                                self.resp_ont_children_ethsvc.append(resp_dict)
                    except:
                        self.resp_ont_children_ethsvc = []
                        if isinstance(resp_dict, list):
                            self.resp_ont_children_ethsvc.extend(resp_dict)
                        else:
                            self.resp_ont_children_ethsvc.append(resp_dict)
                else:
                    pass

                try:
                    resp = self.resp_ont_children_ethsvc
                    del self.resp_ont_children_ethsvc
                except:
                    resp = response
                return resp
            else:
                return response

    def ontprof(self, ontprof_id=""):
        """
        Description
        -----------
        function ontprof() performs a http/xml query for the provided network_nm(e7_node) requesting the children of the <OntProf> object type

        Attributes
        ----------
        :param ontprof_id: this parameter identifies the ID of a pre-defined local ONT profile, which can be a custom profile from 1 to 50, or one of the default profile IDs listed in E7 GPON ONT Profile IDs, as described in pg.140 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type ontprof_id:str

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: ontprof() will return a requests.models.Response object on a failed query, and a dict on a successful query
        """
        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <get-config>
                                    <source>
                                        <running/>
                                    </source>
                                    <filter type="subtree">
                                        <top>
                                            <object>
                                                <type>OntProf</type>
                                                <id>
                                                    <ontprof>{ontprof_id}</ontprof>
                                                </id>
                                            </object>
                                        </top>
                                    </filter>
                                </get-config>
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
            # TODO: IMPLEMENT HTTPS HANDLING
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

    def discont(self, ont_sn=""):
        """
        Description
        -----------
        function discont() performs a http/xml query for the provided network_nm(e7_node) requesting the child of the <DiscOnt> object type

        Attributes
        ----------
        :param ont_sn: this parameter is the SN of the ont being requested, for calix ONTs this is formed by CXNK+
        :type ont_sn:str

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: discont() will return a requests.models.Response object on a failed query, and a dict on a successful query
        """

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <get>
                                    <filter>
                                        <top>
                                            <object>
                                                <type>DiscOnt</type>
                                                <id>
                                                    <discont>{ont_sn}</discont>
                                                </id>
                                            </object>
                                        </top>
                                    </filter>
                                </get>
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
            # TODO: IMPLEMENT HTTPS HANDLING
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

    def ontpwe3prof(self, ontpwe3prof_id="1"):
        """
        Description
        -----------
        function ontpwe3prof() performs a http/xml query for the provided network_nm(e7_node) requesting the <OntPwe3Prof> object type specified by the ontpwe3prof_id provided

        Attributes
        ----------
        :param ontpwe3prof_id: identifies the ID of the profile that sets the ONT PWE3 mode. Use 1 (also the default, if not supplied) for the system-default profile, which is set to use either T1 or E1 mode in the management interface, as described in pg.141 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type ontpwe3prof_id:str

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: ontpwe3prof() will return a requests.models.Response object on a failed query, and a dict on a successful query
        """
        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <get-config>
                                    <source>
                                        <running/>
                                    </source>
                                    <filter type="subtree">
                                        <top>
                                            <object>
                                                <type>OntPwe3Prof</type>
                                                <id>
                                                    <ontpwe3prof>{ontpwe3prof_id}</ontpwe3prof>
                                                </id>
                                            </object>
                                        </top>
                                    </filter>
                                </get-config>
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
            # TODO: IMPLEMENT HTTPS HANDLING
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

    def vlan(self, vlan_id="1"):
        """
        Description
        -----------
        function vlan() performs a http/xml query for the provided network_nm(e7_node) requesting the <Vlan> object type specified by the vlan_id provided

        Attributes
        ----------
        :param vlan_id: Identifies the VLAN: 2 to 4093, excluding any reserved VLANs, as described in pg.50 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type vlan_id:str

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: vlan() will return a requests.models.Response object on a failed query, and a dict on a successful query
        """
        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <get-config>
                                    <source>
                                        <running/>
                                    </source>
                                <filter type="subtree">
                                    <top>
                                        <object>
                                        <type>Vlan</type>
                                            <id>
                                                <vlan>{vlan_id}</vlan>
                                            </id>
                                        </object>
                                    </top>
                                </filter>
                                </get-config>
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
            # TODO: IMPLEMENT HTTPS HANDLING
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

    def ont_ethsvc(
        self, ont_id: str = "", ontslot: str = "3", ontethany: str = "1", ethsvc: str = "1"
    ):
        """
        Description
        -----------
        function ethsvc_ont() performs a http/xml  query for the provided network_nm(e7_node) requesting the current data for the specified ethsvc

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
                                        <get-config>
                                            <source>
                                                <running/>
                                            </source>
                                        <filter type="subtree">
                                            <top>
                                                <object>
                                                    <type>EthSvc</type>
                                                    <id>
                                                        <ont>{ont_id}</ont>
                                                        <ontslot>{ontslot}</ontslot>
                                                        <ontethany>{ontethany}</ontethany>
                                                        <ethsvc>{ethsvc}</ethsvc>
                                                    </id>
                                                </object>
                                            </top>
                                        </filter>
                                        </get-config>
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
            # TODO: IMPLEMENT HTTPS HANDLING
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

    def ont_geth(self, ont_id: str = "", ontethge: str = "1"):
        """
        Description
        -----------
        function ont_geth() performs a http/xml  query for the provided network_nm(e7_node) requesting the current data for the specified ontethge

        Attributes
        ----------
        :param ont_id: Identifies the ONT by its E7 scope ID (1 to 64000000).

        :param ontethge: Identifies the ONT-GE port number (1 to 8).

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection between the client and server times-out

        :return: ont() returns a response.models.Response object on a failed call, and a nested dict on a successful call
        """

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                                        <soapenv:Body>
                                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                                <get-config>
                                                    <source>
                                                        <running/>
                                                    </source>
                                                <filter type="subtree">
                                                    <top>
                                                        <object>
                                                            <type>OntEthGe</type>
                                                            <id>
                                                                <ont>{ont_id}</ont>
                                                                <ontslot>3</ontslot>
                                                                <ontethge>{ontethge}</ontethge>
                                                            </id>
                                                        </object>
                                                    </top>
                                                </filter>
                                                </get-config>
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
            # TODO: IMPLEMENT HTTPS HANDLING
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

    def show_ont(self, action_args={" ": ""}, after_filter={" ": ""}):
        """
        Description
        -----------
        function show_ont() performs the CLI command show-ont for the provided network_nm(e7_node) through a http/xml query

        Attributes
        ----------
        :param action_args: similar to attr_filter param in other query functions, action_args acts as a filter for the query
        :type action_args:dict

        :param after_filter: this parameter is a dict of the child object to input in the <after> element as shown in pg.18 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type after_filter:dict

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: show_ont() returns a list of dicts on a successful call and a requests.models.Response object on a failed call.

        Example
        -----------
        IMPORTANT NOTE

        Once the Query_E7_Data() object is created we can then call the show_ont() function
        show_ont() function can be used to collect the Provisioned ONTs Data on the targeted Network Name(ie..the E7 NODE)
        -----IMPORTANT NOTE-----
        While testing this solution, I discovered a http_timeout of 5, had to be set to prevent a timeout, your mileage may vary

        this base query will pull data for all provisioned ONTs on the targeted Network Name(ie..the E7 NODE)
        query_e7_data.show_ont(cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                               network_nm='NTWK-Example Network Name',
                               http_timeout=5)

        While pulling data for all ONTs on the node can be useful, it is much better to have a more precise query
        for this we can pass filters to the show_ont() function
        ---------LIST OF FILTERS----------
        admin:['enabled', 'enabled-no-alarms', 'disabled']
        serno:'123456'
        subscr-id: '99999'
        reg-id:
        pon:{'shelf': '1', 'card': '1', 'gponport': '1'}
        ontprof: '1'
        ont:'1'

        # In this example we will pull the stats for all provisioned ONTs that are 'enabled'
        query_e7_data.show_ont(cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                               network_nm='NTWK-Example Network Name',
                               http_timeout=5,
                               action_args={'admin': 'enabled'})

        # In this example we will pull the stats for all provisioned ONTs using a specific ontprof
        # IMPORTANT NOTE - submit the ontprof id not the name
        query_e7_data.show_ont(cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                               network_nm='NTWK-Example Network Name',
                               http_timeout=5,
                               action_args={'ontprof': '1'})

        # In this example we will pull the stats for all provisioned ONTs that are on a specific pon port
        # for this example we will be using GPON id 1/1/1
        query_e7_data.show_ont(cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                               network_nm='NTWK-Example Network Name',
                               http_timeout=5,
                               action_args={'pon': {'shelf': '1', 'card': '1', 'gponport': '1'}})

        # In this example we will pull the stats for the specified ONT by its serial-number
        # IMPORTANT NOTE - cms expects the Hexadecimal version of the SN, normally this will be the last 6 char of the serial
        # Say we have a serial of CXNK00123456, we would submit 123456
        query_e7_data.show_ont(cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                               network_nm='NTWK-Example Network Name',
                               http_timeout=5,
                               action_args={'serno': '123456'})

        # In this example we will pull the stats for the specified ONT by its provisioned subscriber-id
        query_e7_data.show_ont(cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                               network_nm='NTWK-Example Network Name',
                               http_timeout=5,
                               action_args={'subscr-id': '99999999'})

        # In this example we will pull the stats for the specified ONT by its ONT ID
        query_e7_data.show_ont(cms_user_nm=client.cms_nbi_config['cms_nodes']['example_node']['cms_creds']['user_nm'],
                               network_nm='NTWK-Example Network Name',
                               http_timeout=5,
                               action_args={'ont': '1'})
        """
        if " " not in after_filter.keys():
            _after_filter = f"""<after>
                                    <type>Ont</type>
                                    <id>
                                        <ont>{after_filter['ont']}</ont>
                                    </id>
                                </after>"""
        else:
            _after_filter = """"""

        valid_action_args = ["admin", "serno", "reg-id", "subscr-id", "pon", "ontprof", "ont"]
        if " " not in action_args.keys():
            _action_args = """"""
            for arg in action_args.items():
                if arg[0] in valid_action_args:
                    if arg[0] == "pon":
                        _action_args = (
                            _action_args
                            + f"""<linked-pon>
                                                          <type>GponPort</type>
                                                          <id>
                                                          <shelf>{arg[1]['shelf']}</shelf>
                                                          <card>{arg[1]['card']}</card>
                                                          <gponport>{arg[1]['gponport']}</gponport>
                                                          </id>
                                                          </linked-pon>"""
                        )
                    elif arg[0] == "ontprof":
                        _action_args = (
                            _action_args
                            + f"""<ontprof>
                                                          <type>OntProf</type>
                                                          <id>
                                                          <ontprof>{arg[1]}</ontprof>
                                                          </id>
                                                          </ontprof>"""
                        )
                    elif arg[0] == "ont":
                        _action_args = (
                            _action_args
                            + f"""<ont>
                                                          <type>Ont</type>
                                                          <id>
                                                          <ont>{arg[1]}</ont>
                                                          </id>
                                                          </ont>"""
                        )
                    else:
                        _action_args = _action_args + f"""<{arg[0]}>{arg[1]}</{arg[0]}>"""
        else:
            _action_args = """"""

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <action>
                                    <action-type>show-ont</action-type>
                                    <action-args>
                                    {_action_args}
                                    {_after_filter}
                                    </action-args>
                                </action>
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
            # TODO: IMPLEMENT HTTPS HANDLING
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response object is returned.
            return response

        else:
            resp_dict = xmltodict.parse(response.content)
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.more"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"][
                    "action-reply"
                ]["match"]
                _after_filter_ = resp_dict["get"]["object"]["id"]
                try:
                    if isinstance(self.resp_show_ont, list):
                        self.resp_show_ont.append(resp_dict)
                except:
                    self.resp_show_ont = []
                    self.resp_show_ont.append(resp_dict)
                return self.show_ont(after_filter=_after_filter_, action_args=action_args)

            elif pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"][
                    "action-reply"
                ]["match"]
                try:
                    if isinstance(self.resp_show_ont, list):
                        self.resp_show_ont.append(resp_dict)
                        resp_show_ont = self.resp_show_ont
                        del self.resp_show_ont
                        return resp_show_ont
                except:
                    self.resp_show_ont = []
                    self.resp_show_ont.append(resp_dict)
                    resp_show_ont = self.resp_show_ont
                    del self.resp_show_ont
                    return resp_show_ont

            elif pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply"
            ):
                try:
                    if isinstance(self.resp_show_ont, list):
                        resp_show_ont = self.resp_show_ont
                        del self.resp_show_ont
                        return resp_show_ont
                except:
                    return response

            else:
                return response

    def show_dhcp_leases(self, action_args={" ": ""}, after_filter={" ": ""}):
        """
        Description
        -----------
        function show_dhcp_leases() performs the CLI command show-dhcp-leases for the provided network_nm(e7_node) through a http/xml query

        Attributes
        ----------
        :param action_args: similar to attr_filter param in other query functions, action_args acts as a filter for the query
        :type action_args:dict

        :param after_filter: this parameter is a dict of the child object to input in the <after> element as shown in pg.18 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type after_filter:dict

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: show_dhcp_leases() returns a list of dicts on a successful call and a requests.models.Response object on a failed call.
        """
        valid_action_args = ["vlan", "ontethge", "ontethfe", "ethintf", "gponport"]
        if " " not in action_args.keys():
            _action_args = """"""
            for arg in action_args.items():
                if arg[0] in valid_action_args:
                    if "vlan" in arg[0]:
                        _action_args += f"""<vlan>{arg[1]}</vlan>"""
                    elif "ontethge" in arg[0]:
                        _action_args += f"""<object>
                                                <type>OntEthGe</type>
                                                <id>
                                                    <ont>{arg[1]['ont']}</ont>
                                                    <ontslot>3</ontslot>
                                                    <ontethge>{arg[1]['ontethge']}</ontethge>
                                                </id>
                                            </object>"""
                    elif "ontethfe" in arg[0]:
                        _action_args += f"""<object>
                                                <type>OntEthFe</type>
                                                <id>
                                                    <ont>{arg[1]['ont']}</ont>
                                                    <ontslot>5</ontslot>
                                                    <ontethfe>{arg[1]['ontethfe']}</ontethfe>
                                                </id>
                                            </object>"""
                    elif "gponport" in arg[0]:
                        _action_args += f"""<object>
                                                <type>GponPort</type>
                                                <id>
                                                    <shelf>{arg[1]['shelf']}</shelf>
                                                    <card>{arg[1]['card']}</card>
                                                    <gponport>{arg[1]['gponport']}</gponport>
                                                </id>
                                            </object>"""
                    elif "ethintf" in arg[0]:
                        _action_args += f"""<object>
                                                <type>EthIntf</type>
                                                <id>
                                                    <shelf>{arg[1]['shelf']}</shelf>
                                                    <card>{arg[1]['card']}</card>
                                                    <ethintf>{arg[1]['ethintf']}</ethintf>
                                                </id>
                                            </object>"""
                    else:
                        pass
                else:
                    pass
        else:
            _action_args = """"""

        if " " not in after_filter.keys():
            _after_filter = (
                f"""<after>{xmltodict.unparse(after_filter, full_document=False)}</after>"""
            )
        else:
            _after_filter = """"""

        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <action>
                                    <action-type>show-dhcp-leases</action-type>
                                    <action-args>
                                    {_action_args}
                                    {_after_filter}
                                    </action-args>
                                </action>
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
            # TODO: IMPLEMENT HTTPS HANDLING
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response object is returned.
            return response

        else:
            resp_dict = xmltodict.parse(response.content)
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.more"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"][
                    "action-reply"
                ]["entry"]
                _after_filter_ = resp_dict[len(resp_dict) - 1]
                try:
                    if isinstance(self.resp_show_dhcp_leases, list):
                        self.resp_show_dhcp_leases.extend(resp_dict)
                except NameError:
                    self.resp_show_dhcp_leases = []
                    self.resp_show_dhcp_leases.extend(resp_dict)
                return self.show_dhcp_leases(action_args=action_args, after_filter=_after_filter_)
            elif pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.entry"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"][
                    "action-reply"
                ]["entry"]
                try:
                    if isinstance(self.resp_show_dhcp_leases, list):
                        if isinstance(resp_dict, list):
                            self.resp_show_dhcp_leases.extend(resp_dict)
                        else:
                            self.resp_show_dhcp_leases.append(resp_dict)
                except NameError:
                    self.resp_show_dhcp_leases = []
                    if isinstance(resp_dict, list):
                        self.resp_show_dhcp_leases.extend(resp_dict)
                    else:
                        self.resp_show_dhcp_leases.append(resp_dict)
                resp = self.resp_show_dhcp_leases
                del self.resp_show_dhcp_leases
                return resp
            else:
                return response

    def show_vlan_members(self, vlan_id="1", after_filter={" ": ""}):
        """
        Description
        -----------
        function show_vlan_members() performs the CLI command show-vlan-members for the provided network_nm(e7_node) through a http/xml query

        Attributes
        ----------
        :param vlan_id: the vlan id
        :type vlan_id:str

        :param after_filter: this parameter is a dict of the child object to input in the <after> element as shown in pg.18 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type after_filter:dict

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: show_vlan_members() returns a list of dicts on a successful call and a requests.models.Response object on a failed call.
        """
        if " " not in after_filter.keys():
            _after_filter = (
                f"""<after>{xmltodict.unparse(after_filter, full_document=False)}</after>"""
            )
        else:
            _after_filter = """"""
        payload = f"""<soapenv:Envelope xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
                        <soapenv:Body>
                            <rpc message-id="{self.message_id}" nodename="{self.network_nm}" username="{self.cms_user_nm}" sessionid="{self.client_object.session_id}">
                                <action>
                                    <action-type>show-vlan-intforeaps</action-type>
                                    <action-args>
                                        <object>
                                            <type>Vlan</type>
                                            <id>
                                                <vlan>{vlan_id}</vlan>
                                            </id>
                                        </object>
                                        {_after_filter}
                                    </action-args>
                                </action>
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
            # TODO: IMPLEMENT HTTPS HANDLING
            pass

        if response.status_code != 200:
            # if the response code is not 200 FALSE and the request.response object is returned.
            return response

        else:
            resp_dict = xmltodict.parse(response.content)
            if pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.more"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"][
                    "action-reply"
                ]["match"]
                __after_filter = resp_dict[len(resp_dict) - 1]
                try:
                    if isinstance(self.resp_show_vlan_members, list):
                        self.resp_show_vlan_members.extend(resp_dict)
                except:
                    self.resp_show_vlan_members = []
                    self.resp_show_vlan_members.extend(resp_dict)
                return self.show_vlan_members(vlan_id=vlan_id, after_filter=__after_filter)
            elif pydash.objects.has(
                resp_dict, "soapenv:Envelope.soapenv:Body.rpc-reply.action-reply.match"
            ):
                resp_dict = resp_dict["soapenv:Envelope"]["soapenv:Body"]["rpc-reply"][
                    "action-reply"
                ]["match"]
                try:
                    if isinstance(self.resp_show_vlan_members, list):
                        if isinstance(resp_dict, list):
                            self.resp_show_vlan_members.extend(resp_dict)
                        else:
                            self.resp_show_vlan_members.append(resp_dict)
                except:
                    self.resp_show_vlan_members = []
                    if isinstance(resp_dict, list):
                        self.resp_show_vlan_members.extend(resp_dict)
                    else:
                        self.resp_show_vlan_members.append(resp_dict)
                resp = self.resp_show_vlan_members
                del self.resp_show_vlan_members
                return resp
            else:
                return response
