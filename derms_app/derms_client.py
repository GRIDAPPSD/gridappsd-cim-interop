import datetime
import logging
from lxml import etree
import xml.etree.ElementTree as ET
import uuid

from zeep import Client, helpers
from zeep.plugins import HistoryPlugin

from derms_app import constants as c
from derms_app.equipment import Equipment, SynchronousMachine, Solar, Battery

_log = logging.getLogger(__name__)


def __build_endpoint_header(verb, message_id=None, correlation_id=None):
    '''
    create message header
    :param verb: string. create, change, delete execute, get , reply, etc.
    :param message_id: string. UUID
    :param correlation_id: string. UUID
    :return: json string as the header
    '''
    message_id = message_id if message_id is not None else uuid.uuid4()
    correlation_id = correlation_id if correlation_id is not None else uuid.uuid4()

    return {
        "Verb": verb,
        "Noun": "DERGroups",
        "Timestamp": datetime.datetime.now(),
        "MessageID": message_id,
        "CorrelationID": correlation_id
    }


def __build_der_function(derFunctions):
    '''
    create the DERFunction json string
    :param connectDisconnect:
    :param frequencyWattCurveFunction:
    :param maxRealPowerLimiting:
    :param rampRateControl:
    :param reactivePowerDispatch:
    :param voltageRegulation:
    :param realPowerDispatch:
    :param voltVarCurveFunction:
    :param voltWattCurveFunction:
    :return: json string
    '''
    return {
        "connectDisconnect": str(derFunctions.connectDisconnect).lower(),
        "frequencyWattCurveFunction": str(derFunctions.frequencyWattCurveFunction).lower(),
        "maxRealPowerLimiting": str(derFunctions.maxRealPowerLimiting).lower(),
        "rampRateControl": str(derFunctions.rampRateControl).lower(),
        "reactivePowerDispatch": str(derFunctions.reactivePowerDispatch).lower(),
        "voltageRegulation": str(derFunctions.voltageRegulation).lower(),
        "realPowerDispatch": str(derFunctions.realPowerDispatch).lower(),
        "voltVarCurveFunction": str(derFunctions.voltVarCurveFunction).lower(),
        "voltWattCurveFunction": str(derFunctions.voltWattCurveFunction).lower()
    }


def __build_enddevice_group(mrid, name, description, devices_mrid_list, derFunctions):
    '''
    create one EndDeviceGroup json string
    :param mrid: string
    :param name: string
    :param devices_mrid_list: list of type Device
    :return: json string represent a end device group
    '''
    return {
        "mRID": mrid,
        "description": description,
        "DERFunction": __build_der_function(derFunctions),
        "EndDevices": devices_mrid_list,
        "Names": __build_names(name),
        "version": {
            "date": "2017-05-31T13:55:01-06:00",
            "major": 1,
            "minor": 0,
            "revision": 0
        }
    }


def __build_names(name):
    '''
    create the Names json string
    :param names: string
    :return: json string
    '''
    # if not isinstance(names, list):
    #     names = [names]
    #
    # name_list = []
    # for name in names:
    #     name_list.append({"name": name})
    # return name_list
    return {"name": name};


def __get_create_body(mrid, name, device_mrid_list):
    '''
    create message body with only 1 group
    :param mrid: string
    :param name: string
    :param device_mrid_list: Lis of type Device
    :return: json string
    '''
    devices_mrid_list = [{"mRID": x} for x in device_mrid_list] # this creates a list of with the same key, could cause problem?
    body = {
        "DERGroups": [{
            "EndDeviceGroup": __build_enddevice_group(mrid, name, devices_mrid_list)
        }]
    }
    return body


def __get_create_body_group(group):
    end_device_group = []
    devices_mrid_list = [{"mRID": x.mRID} for x in group.devices]
    end_device_group.append(__build_enddevice_group(group.mrid, group.name, group.description, devices_mrid_list, group.derFunctions))
    body = {
        "DERGroups": {
            "EndDeviceGroup": end_device_group
        }
    }
    return body


def __get_create_body_groups(group_list):
    '''
    create the body of the message using the list of the groups that need to be created
    :param group_list: list of groups
    :return: json string of DERGroups
    '''
    # create dictionary of lists of EndDeviceGroup
    end_device_group = []
    for grp in group_list:
        # this creates a list of with the same key, could cause problem, actually, it does not cause problem, and better than the later way
        devices_mrid_list = [{"mRID": x} for x in grp.devices]
        end_device_group.append(__build_enddevice_group(grp.mrid, grp.name, grp.description, devices_mrid_list, grp.derFunctions))
    body = {
        "DERGroups": {
            "EndDeviceGroup": end_device_group
        }
    }

    # create list of dictionary of EndDeviceGroup, which would be duplicate keys in the dictionary, it might not work
    # derGroups=[]
    # for grp in group_list:
    #     derGroups.append({"EndDeviceGroup": __build_enddevice_group(grp.mrid, grp.name, grp.devices)})
    # body = {
    #     "DERGroups": derGroups
    # }

    return body


def __build_query_request_byNames(names):
    groups = []
    for name in names:
        groups.append({'Names': {'name': name}})
    # only this way works, i.e., 'EndDeviceGroup' is a list of dictionary
    # if I put 'EndDeviceGroup' in front of each 'Names' to form a list of EndDeviceGroup dictionary,
    # it won't work for multiples of EndDeviceGroup
    request = {
        # 'ID': uuid.uuid4(),
        # 'StartTime': datetime.datetime.now(),
        # 'EndTime': datetime.datetime.now(),
        'DERGroupQueries': {
            'EndDeviceGroup': groups
        }
    }
    return request


def __build_query_request_bymRIDs(mrids):
    groups = []
    for mrid in mrids:
        groups.append({'mRID': mrid})
    # only this way works, i.e., 'EndDeviceGroup' is a list of dictionary
    # if I put 'EndDeviceGroup' in front of each 'Names' to form a list of EndDeviceGroup dictionary,
    # it won't work for multiples of EndDeviceGroup
    request = {
        # 'ID': uuid.uuid4(),
        # 'StartTime': datetime.datetime.now(),
        # 'EndTime': datetime.datetime.now(),
        'DERGroupQueries': {
            'EndDeviceGroup': groups
        }
    }
    return request


def get_devices():
    history = HistoryPlugin()
    client = Client(c.GET_DEVICE_ENDPOINT, plugins=[history])
    # with client.settings(raw_response=True):
    #     r = client.service.GetDevices()
    # print(client.wsdl.bindings)
    r = client.service.GetDevices()
    deviceList = r
    # for d in r.synchronousMachines.SynchronousMachine:
    #     deviceList.append(d)
    # for d in r.solars.Solar:
    #     deviceList.append(d)
    # for d in r.batteries.Battery:
    #     deviceList.append(d)

    # for deviceType in r:
        # print(deviceType.tag)
        # print(type(deviceType))
        # data = deviceType.find('data')
        # results = data.find('results')
        # for binding in results:
        #     # name = binding.find('name').findtext('value')
        #     for attribute in binding:
        #         # print(attribute.tag, attribute.text)
        #         if attribute.tag == "name":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     name = item2.text
        #         elif attribute.tag == "bus":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     bus = item2.text
        #         elif attribute.tag == "phases":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     phases = item2.text
        #         elif attribute.tag == "ratedS":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     ratedS = item2.text
        #         elif attribute.tag == "ratedU":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     ratedU = item2.text
        #         elif attribute.tag == "p":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     p = item2.text
        #         elif attribute.tag == "q":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     q = item2.text
        #         elif attribute.tag == "id":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     id = item2.text
        #         elif attribute.tag == "fdrid":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     fdrid = item2.text
        #         elif attribute.tag == "ipu":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     ipu = item2.text
        #         elif attribute.tag == "ratedE":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     ratedE = item2.text
        #         elif attribute.tag == "storedE":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     storedE = item2.text
        #         elif attribute.tag == "state":
        #             for item2 in attribute:
        #                 if item2.tag == 'value':
        #                     state = item2.text
        #     if deviceType.tag == 'SynchronousMachine':
        #         newDevice = SynchronousMachine(name, bus, ratedS, ratedU, p, q, id, fdrid, phases)
        #         deviceList.append(newDevice)
        #     if deviceType.tag == 'Solar':
        #         newDevice = Solar(name, bus, ratedS, ratedU, ipu, p, q, fdrid, phases)
        #         deviceList.append(newDevice)
        #     if deviceType.tag == 'Battery':
        #         newDevice = Battery(name, bus, ratedS, ratedU, ipu, ratedE, storedE, state, p, q, id, fdrid, phases)
        #         deviceList.append(newDevice)

    _log.debug("Data Sent:\n{}".format(etree.tounicode(history.last_sent['envelope'], pretty_print=True)))
    _log.debug("Data Response:\n{}".format(etree.tounicode(history.last_received['envelope'], pretty_print=True)))
    return deviceList


# def create_group(mrid, name, device_mrid_list):
#     '''
#     create one group
#     :param mrid: string
#     :param name: string
#     :param device_mrid_list: List of type Device
#     :return: response from the server
#     '''
#     history = HistoryPlugin()
#     client = Client(c.CREATE_DERGROUP_ENDPOINT, plugins=[history])
#     headers = __build_endpoint_header("create")
#     body = __get_create_body(mrid, name, device_mrid_list)
#     from pprint import pprint
#     print("HEADERS")
#     pprint(headers)
#     print("BODY")
#     pprint(body)
#     response = get_service(client, "create").CreateDERGroups(Header=headers, Payload=body)
#     _log.debug("Data Sent:\n{}".format(etree.tounicode(history.last_sent['envelope'], pretty_print=True)))
#     #_log.debug("ZEEP Respons:\n{}".format(response))
#     _log.debug("Data Response:\n{}".format(etree.tounicode(history.last_received['envelope'], pretty_print=True)))
#
#     return response


def create_groups(group_list):
    '''
    create multiple group
    :param group_list: List of type Group
    :return: response from the server
    '''
    history = HistoryPlugin()
    client = Client(c.CREATE_DERGROUP_ENDPOINT, plugins=[history])
    headers = __build_endpoint_header("CREATE")
    body = __get_create_body_groups(group_list)
    from pprint import pprint
    print("HEADERS")
    pprint(headers)
    print("BODY")
    pprint(body)
    response = get_service(client, "CREATE").CreateDERGroups(Header=headers, Payload=body)
    _log.debug("Data Sent:\n{}".format(etree.tounicode(history.last_sent['envelope'], pretty_print=True)))
    #_log.debug("ZEEP Respons:\n{}".format(response))
    _log.debug("Data Response:\n{}".format(etree.tounicode(history.last_received['envelope'], pretty_print=True)))

    return response


def get_service(client, verb):
    '''
    create service
    :param client:
    :param verb: string. create, delete, get, etc.
    :return: the ServiceProxy object that is created in the Client object
    '''
    bindings = c.SOAP_BINDINGS[verb]
    service = client.create_service(*bindings) # here * is for unpacking
    return service


def create_multiple_group(mrid_list, name_list, device_mrid_list_list):
    '''
    create multiple groups
    :param mrid_list: List of string
    :param name_list: List of string
    :param device_mrid_list_list: List of list of type Device
    :return: response from the server
    '''
    assert len(mrid_list) == len(name_list) == len(device_mrid_list_list), "Passed lists must be the same length"

    headers = __build_endpoint_header("create")
    body = None

    for i in range(len(mrid_list)):
        if body is None:
            body = __get_create_body(mrid_list[i], name_list[i], device_mrid_list_list[i])
        else:
            new_group = {
                "EndDeviceGroup": __build_enddevice_group(mrid_list[i], name_list[i], device_mrid_list_list[i])
            }
            body["DERGroups"].append(new_group)

    history = HistoryPlugin()
    client = Client(c.CREATE_DERGROUP_ENDPOINT, plugins=[history])
    # node = client.create_message(client.service, 'CreateDERGroups', Header=headers, Payload=body)
    # print(node)

    response = client.service.CreateDERGroups(Header=headers, Payload=body)
    _log.debug("Data Sent:\n{}".format(etree.tounicode(history.last_sent['envelope'], pretty_print=True)))
    # _log.debug("ZEEP Respons:\n{}".format(response))
    _log.debug("Data Response:\n{}".format(etree.tounicode(history.last_received['envelope'], pretty_print=True)))

    return response


# def get_end_device_groups():
#     history = HistoryPlugin()
#     client = Client(c.QUERY_DERGROUP_ENDPOINT, plugins=[history])
#     r = client.service.GetDERGroups()
#     print(r)
#     return r


def query_groups_byName(names):
    headers = __build_endpoint_header("GET")
    request = __build_query_request_byNames(names)
    print(request)
    history = HistoryPlugin()
    client = Client(c.QUERY_DERGROUP_ENDPOINT, plugins=[history])
    try:
        response = get_service(client, "GET").QueryDERGroups(headers, request)
    except Exception as e:
        raise e
    # try:
    #     response = client.service.QueryDERGroups(Header=headers, Request=request)
    # except Exception as e:
    #     pass
    _log.debug("Data Sent:\n{}".format(etree.tounicode(history.last_sent['envelope'], pretty_print=True)))
    _log.debug("Data Response:\n{}".format(etree.tounicode(history.last_received['envelope'], pretty_print=True)))
    return response


def query_groups_bymRID(mrids):
    headers = __build_endpoint_header("GET")
    request = __build_query_request_bymRIDs(mrids)
    history = HistoryPlugin()
    client = Client(c.QUERY_DERGROUP_ENDPOINT, plugins=[history])
    try:
        response = get_service(client, "GET").QueryDERGroups(headers, request)
    except Exception as e:
        raise e
    return response


def query_all_groups():
    headers = __build_endpoint_header("GET")
    print(headers)
    request = {
        'DERGroupQueries': {
            'EndDeviceGroup': {}
        }
    }
    print(request)
    history = HistoryPlugin()
    client = Client(c.QUERY_DERGROUP_ENDPOINT, plugins=[history])
    try:
        response = get_service(client, "GET").QueryDERGroups(headers, request)
    except Exception as e:
        raise e
    return response


def modify_a_group(originalgroup, modifiedgroup):
    history = HistoryPlugin()
    client = Client(c.CHANGE_DERGROUP_ENDPOINT, plugins=[history])
    # can compare the original with modified to find out if derfunction changed, make payload only contain derfunctions
    # can compare the original with modified to find out if der devices changed, make payload only the added device mrid
    # do the above and delete the missing device
    # however, since the epri test harness cannot distinguish the payload, I will just put everything in
    # _compare_der_functions(originalgroup, modifiedgroup)
    headers = __build_endpoint_header("CHANGE")
    payload = __get_create_body_group(modifiedgroup)
    from pprint import pprint
    print("HEADERS")
    pprint(headers)
    print("PAYLOAD")
    pprint(payload)
    response = get_service(client, "CHANGE").ChangeDERGroups(Header=headers, Payload=payload)
    _log.debug("Data Sent:\n{}".format(etree.tounicode(history.last_sent['envelope'], pretty_print=True)))
    _log.debug("Data Response:\n{}".format(etree.tounicode(history.last_received['envelope'], pretty_print=True)))
    return response


def change_group(mrid, name, device_mrid_list):
    headers = __build_endpoint_header("create")
    body = None

    history = HistoryPlugin()
    client = Client(c.CHANGE_DERGROUP_ENDPOINT, plugins=[history])
    # node = client.create_message(client.service, 'CreateDERGroups', Header=headers, Payload=body)
    # print(node)

    response = client.service.ChangeDERGroups(Header=headers, Payload=body)
    _log.debug("Data Sent:\n{}".format(etree.tounicode(history.last_sent['envelope'], pretty_print=True)))
    # _log.debug("ZEEP Respons:\n{}".format(response))
    _log.debug("Data Response:\n{}".format(etree.tounicode(history.last_received['envelope'], pretty_print=True)))


def delete_group(name=None, mrid=None):
    assert name or mrid, "Must have either name or mrid specified"
    assert not (name and mrid), "Must have either name or mrid specified"
    headers = __build_endpoint_header("DELETE")
    if name:
        body = {
            "DERGroups": [
                {"EndDeviceGroup": {"Names": __build_names(name)}}
            ]
        }
    else:
        body = {
            "DERGroups": [
                {"EndDeviceGroup": {"mRID": str(mrid)}}
            ]
        }
    message = {"Header": headers, "Payload": body}
    print(message)
    history = HistoryPlugin()
    client = Client(c.CHANGE_DERGROUP_ENDPOINT, plugins=[history])
    # node = client.create_message(client.service, 'CreateDERGroups', Header=headers, Payload=body)
    # print(node)

    response = get_service(client, "DELETE").DeleteDERGroups(Header=headers, Payload=body)
    _log.debug("Data Sent:\n{}".format(etree.tounicode(history.last_sent['envelope'], pretty_print=True)))
    # _log.debug("ZEEP Respons:\n{}".format(response))
    _log.debug("Data Response:\n{}".format(etree.tounicode(history.last_received['envelope'], pretty_print=True)))

    return response


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    from derms_app.createDeviceJsonConf import Device

#     def duplicate_group_test():
#         mrid = uuid.uuid4()
#         dev_list = [Equipment("2fabd157-a01c-4f87-b4a0-2ee92989766b", "dnp3_010", "atype").mrid,
#                     Equipment("8ac14ae9-9c13-4202-8fa2-944dd4a18029", "dnp3_011", "atype").mrid,
#                     Equipment("4c2a89bc-377a-47cb-ab17-c1462da33760", "dnp3_012", "atype").mrid]
#         response1 = create_group(mrid, "a group 6", dev_list)
#         assert response1 is not None, "Invalid response received"
#         assert response1.Reply.Result == "OK", "Failed to create first group perhaps the start state is invalid"
#         response2 = create_group(mrid, "a group 6", dev_list)
#
#         if response2.Reply.Result == 'FAILED':
#             _log.info("Success")
#         else:
#             _log.info("Failed")
#
#
#     menu = """
# Select from the following tests:
#
#     1  Create Multiple
#     h  Repeat Menu
#     q  Quit
# """
#     print(menu)
#     while True:
#         choice = input(">")
#         if choice not in ('1', 'h', 'q'):
#             print(f"Invalid option choice {choice}")
#             continue
#
#         if choice == 'q' or choice == 'Q':
#             break
#         elif choice == 'h' or choice == 'H':
#             print(menu)
#         elif choice == '1':
#             duplicate_group_test()



    # Now go for multiple creations
    # mrids = [uuid.uuid4(), uuid.uuid4()]
    # names = ["alpha", "beta"]
    # list_of_lists = [
    #     [
    #         Device(uuid.uuid4(), "foo", "atype"),
    #         Device(uuid.uuid4(), "bar", "atype"),
    #         Device(uuid.uuid4(), "bim", "atype")
    #     ],
    #     [
    #         Device(uuid.uuid4(), "fat", "atype"),
    #         Device(uuid.uuid4(), "cow", "atype"),
    #         Device(uuid.uuid4(), "rus", "atype")
    #     ]
    # ]
    #
    # create_multiple_group(mrids, names, list_of_lists)

    # delete_group(name="DG1")
    #vdelete_group(mrid=uuid.uuid4())
#    delete_group("DG1")