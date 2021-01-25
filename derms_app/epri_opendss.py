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
GET_DEVICE_ENDPOINT = f"{BASE_URL}/get/getDevices?wsdl"
GET_DEVICE_SOAP_BINDING = (
        f'{{{Namespace_URL}}}GetDevicesService',
        f"{BASE_URL}/get/getDevices"
)
GET_DERGROUPS_ENDPOINT = f"{BASE_URL}/get/getDERGroups?wsdl"

CREATE_DERGROUP_ENDPOINT = f"{BASE_URL}/create/executeDERGroups?wsdl"
CREATE_NAMESPACE_SOAP_BINDING = (
        f'{{{Namespace_URL}}}CreateDERGroupsService',
        f"{BASE_URL}/create/executeDERGroups"
)
CHANGE_DERGROUP_ENDPOINT = f"{BASE_URL}/change/executeDERGroups?wsdl"
CHANGE_NAMESPACE_SOAP_BINDING = (
        f'{{{Namespace_URL}}}ExecuteDERGroupsService',
        f"{BASE_URL}/change/executeDERGroups"
)
QUERY_DERGROUP_ENDPOINT = f"{BASE_URL}/get/queryDERGroups?wsdl"
QUERY_NAMESPACE_SOAP_BINDING = (
        f'{{{Namespace_URL}}}QueryDERGroupsService',
        f'{BASE_URL}/get/queryDERGroups'
)
QUERY_DERGROUP_STATUS_ENDPOINT = f"{BASE_URL}/get/queryDERGroupStatuses?wsdl"
QUERY_NAMESPACE_STATUS_SOAP_BINDING = (
        f'{{{Namespace_URL}}}QueryDERGroupStatusesService',
        f'{BASE_URL}/get/queryDERGroupStatuses'
)