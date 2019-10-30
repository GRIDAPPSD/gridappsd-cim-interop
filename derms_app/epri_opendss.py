#constants for gridappsD opendss bindings
BASE_URL = "http://172.20.10.6:9000"
CREATE_DERGROUP_ENDPOINT = f"{BASE_URL}/service/org/epri/dergroups/create?wsdl"
CREATE_NAMESPACE_SOAP_BINDING = (
        '{http://iec.ch/TC57/2017/ExecuteDERGroups}ExecuteDERGroupsSoapBinding',
        'http://172.20.10.6:9000/service/org/epri/dergroups/create'
)
CHANGE_DERGROUP_ENDPOINT = f"{BASE_URL}/service/org/epri/dergroups/change?wsdl"
CHANGE_NAMESPACE_SOAP_BINDING = (
    '{http://iec.ch/TC57/2017/ExecuteDERGroups}ExecuteDERGroupsSoapBinding',
    'http://172.20.10.6:9000/service/org/epri/dergroups/change'
)