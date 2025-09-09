# IMPORT STATEMENTS
import requests

from ..client import Client  # Import Client from relative path to avoid circular import

# IMPORT STATEMENTS


class Query:
    def __init__(self, cms_nbi_connect_object):
        """
        Description
        -----------
        Class (Query) is the REST query constructor/posting class for the CMS REST NBI

        Attributes
        ----------
        :var self.cms_nbi_connect_object: accepts object created by the CMS_NBI_Client
        :type self.cms_nbi_connect_object: object
        """
        # Test if the provided object is of a Client instance or CMSClient
        # Import at runtime to avoid circular imports
        from ..client_v2 import CMSClient

        if isinstance(cms_nbi_connect_object, (Client, CMSClient)):
            pass
        else:
            raise ValueError(
                f"""Query accepts a instance of Client or CMSClient, a instance of {type(cms_nbi_connect_object)}"""
            )
        self.cms_nbi_connect_object = cms_nbi_connect_object

    def device(
        self,
        protocol="http",
        port="8080",
        cms_user_nm="rootgod",
        cms_user_pass="root",
        cms_node_ip="localhost",
        device_type="",
        http_timeout=1,
    ):
        """
        Description
        -----------
        function device() performs a HTTP GET utilizing the request library to query the CMS REST NBI for the specified devices, as explained in pg.378 of Calix Management System (CMS) R15.x Northbound Interface API Guide

        Parameter(s)
        ------------
        :param protocol: this var determines the protocol to use when building the CMS REST NBI URL, CMS supports http/s as described in pg.14 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type protocol:str

        :param port: this var determines the TCP/UDP port to use when building the CMS REST NBI URL, this will be dependent on whether HTTP or HTTPS was chosen, this is described in pg.14 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type port:str

        :param cms_user_nm: this var contains the username for the CMS USER ACCOUNT utilized in the interactions, this is described in pg.15 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type cms_user_nm:str

        :param cms_user_pass: this var contains the plain text password for the provided username, this is described in pg.15 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type cms_user_pass:str

        :param cms_node_ip: this var contains the FQDN/IP of the targeted CMS node
        :type cms_node_ip:str

        :param device_type: device type is a str identifying the targeted device type, this is explained further in pg.378 of Calix Management System (CMS) R15.x Northbound Interface API Guide
        :type device_type:str

        :param http_timeout: this var contains the http_timeout for the request library, this is in the form of an int
        :type http_timeout:int

        :raise:
            ConnectTimeout: Will be raised if the http(s) connection timesout

        :return: device() returns a list of nested dicts on a successful query and a request.models.Requests object on failed queries

        Example
        ----------------
        # Create the CMS_NBI_Client() instance
        client = CMS_NBI_Client()

        # While the Query_E7_Data interacts with CMS' NETCONF interface, Query_Rest_Data interacts with CMS REST interface and
        # returns the data in a json format

        # Next we create a Query instance and pass the CMS_NBI_Client instance to it
        Query = Query(client)

        # Once the Query_Rest_Data() instance is created we can call the device() function to query for all nodes with the matching device type

        # QUERY FOR E7 Nodes
        query.device(protocol='http', port='8080', cms_user_nm=client.cms_nbi_config['example_node']['cms_creds']['user_nm'],
                               cms_user_pass=client.cms_nbi_config['example_node']['cms_creds']['pass_wd'],
                               cms_node_ip=client.cms_nbi_config['example_node']['cms_nodes']['example_node']['connection']['cms_node_ip'],
                               device_type='e7',
                               http_timeout=5)

        # QUERY FOR C7 Nodes
        query.device(protocol='http', port='8080', cms_user_nm=client.cms_nbi_config['example_node']['cms_creds']['user_nm'],
                               cms_user_pass=client.cms_nbi_config['example_node']['cms_creds']['pass_wd'],
                               cms_node_ip=client.cms_nbi_config['example_node']['cms_nodes']['example_node']['connection']['cms_node_ip'],
                               device_type='c7',
                               http_timeout=5)
        """
        cms_rest_url = f"""{protocol}://{cms_node_ip}:{port}{self.cms_nbi_connect_object.cms_nbi_config['cms_rest_uri']['devices']}{device_type}&limit=9999"""

        payload = ""

        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"CMS_NBI_CONNECT-{cms_user_nm}",
        }

        try:
            response = requests.get(
                url=cms_rest_url,
                headers=headers,
                data=payload,
                auth=(cms_user_nm, cms_user_pass),
                timeout=http_timeout,
            )
        except requests.exceptions.Timeout as e:
            raise e

        if response.status_code == 200:
            return response.json()["data"]
        else:
            return response
