
BASE_URL = "http://18.216.194.249:8080"
CREATE_DERGROUP_ENDPOINT = f"{BASE_URL}/61968-5/create/executeDERGroups?wsdl"
CHANGE_DERGROUP_ENDPOINT = f"{BASE_URL}/61968-5/change/executeDERGroups?wsdl"
CREATE_NAMESPACE_SOAP_BINDING = (
        '{http://create.ws.server.sixthc.com/}ExecuteDERGroupsServiceSoapBinding',
        f'{BASE_URL}/61968-5/create/executeDERGroups'
)
CHANGE_NAMESPACE_SOAP_BINDING = (
        '{http://change.ws.server.sixthc.com/}ExecuteDERGroupsServiceSoapBinding',
        f'{BASE_URL}/61968-5/change/executeDERGroups'
)