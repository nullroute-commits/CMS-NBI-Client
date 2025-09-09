# IMPORT STATEMENT
from CMSNBIClient import CMS_NBI_Client

# IMPORT STATEMENT

# Create the CMS_NBI_Client() instance
client = CMS_NBI_Client()
# DEFAULT CONFIG CREATED WHEN CMS_NBI_Client() is first called
# {'cms_netconf_uri': {'ae_ont': '/cmsae/ae/netconf',
#                      'c7/e3/e5-100': '/cmsweb/nc',
#                      'e7': '/cmsexc/ex/netconf'},
#  'cms_nodes': {'default': {'cms_creds': {'pass_wd': 'root',
#                                          'user_nm': 'rootgod'},
#                            'connection': {'cms_node_ip': 'localhost',
#                                           'http_timeout': 500,
#                                           'netconf_http_port': '18080',
#                                           'netconf_https_port': '18443',
#                                           'protocol': {'http': 'http',
#                                                        'https': 'https'},
#                                           'rest_http_port': '8080'}}},
#  'cms_rest_uri': {'devices': '/restnbi/devices?deviceType=',
#                   'profile': '/restnbi/profiles?profileType=',
#                   'region': '/restnbi/region',
#                   'topology': '/restnbi/toplinks'}}
# Now let's add a new CMS node to the running config
client.update_config(
    pass_wd="example_pass",
    user_nm="example_user",
    cms_node_name="example_node",
    cms_node_ip="cms.example.com",
)
# UPDATED CONFIG after calling update_config()
# {'cms_netconf_uri': {'ae_ont': '/cmsae/ae/netconf',
#                      'c7/e3/e5-100': '/cmsweb/nc',
#                      'e7': '/cmsexc/ex/netconf'},
#  'cms_nodes': {'default': {'cms_creds': {'pass_wd': 'root',
#                                          'user_nm': 'rootgod'},
#                            'connection': {'cms_node_ip': 'localhost',
#                                           'http_timeout': 500,
#                                           'netconf_http_port': '18080',
#                                           'netconf_https_port': '18443',
#                                           'protocol': {'http': 'http',
#                                                        'https': 'https'},
#                                           'rest_http_port': '8080'}},
#                'example_node': {'cms_creds': {'pass_wd': 'example_pass',
#                                               'user_nm': 'example_user'},
#                                 'connection': {'cms_node_ip': 'cms.example.com',
#                                                'http_timeout': 500,
#                                                'netconf_http_port': '18080',
#                                                'netconf_https_port': '18443',
#                                                'protocols': {'http': 'http',
#                                                              'https': 'https'},
#                                                'rest_http_port': '8080'}}},
#  'cms_rest_uri': {'devices': '/restnbi/devices?deviceType=',
#                   'profile': '/restnbi/profiles?profileType=',
#                   'region': '/restnbi/region',
#                   'topology': '/restnbi/toplinks'}}
# Currently only adding(create) a node is available, will add create/update(merge)/delete functionality later
