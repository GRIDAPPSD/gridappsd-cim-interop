#constants for gridappsD opendss bindings
# BASE_URL = "http://172.20.10.6:9000"
# CREATE_DERGROUP_ENDPOINT = f"{BASE_URL}/service/org/epri/dergroups/create?wsdl"
# CREATE_NAMESPACE_SOAP_BINDING = (
#         '{http://iec.ch/TC57/2017/ExecuteDERGroups}ExecuteDERGroupsSoapBinding',
#         'http://172.20.10.6:9000/service/org/epri/dergroups/create'
# )
# CHANGE_DERGROUP_ENDPOINT = f"{BASE_URL}/service/org/epri/dergroups/change?wsdl"
# CHANGE_NAMESPACE_SOAP_BINDING = (
#     '{http://iec.ch/TC57/2017/ExecuteDERGroups}ExecuteDERGroupsSoapBinding',
#     'http://172.20.10.6:9000/service/org/epri/dergroups/change'
# )

# test my soap server binding
BASE_URL = "http://127.0.0.1:8008"
Namespace_URL = 'der.pnnl.gov'
GET_DEVICE_ENDPOINT = f"{BASE_URL}/getDevices?wsdl"
GET_DEVICE_SOAP_BINDING = (
        f'{{{Namespace_URL}}}GetDevicesService',
        f"{BASE_URL}/getDevices"
)
GET_DERGROUPS_ENDPOINT = f"{BASE_URL}/getDERGroups?wsdl"

CREATE_DERGROUP_ENDPOINT = f"{BASE_URL}/createDERGroups?wsdl"
CREATE_NAMESPACE_SOAP_BINDING = (
        f'{{{Namespace_URL}}}CreateDERGroupsService',
        f"{BASE_URL}/createDERGroups"
)
CHANGE_DERGROUP_ENDPOINT = f"{BASE_URL}/createDERGroups?wsdl"
CHANGE_NAMESPACE_SOAP_BINDING = (
    '{http://iec.ch/TC57/2017/ExecuteDERGroups}ExecuteDERGroupsSoapBinding',
        f"{BASE_URL}/ExecuteDERGroupsPort1"
)