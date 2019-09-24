import datetime
import logging
from lxml import etree
import uuid

from zeep import Client
from zeep.plugins import HistoryPlugin

from derms_app import constants as c

_log = logging.getLogger(__name__)


def __build_endpoint_header(verb, message_id=None, correlation_id=None):
    message_id = message_id if message_id is not None else uuid.uuid4()
    correlation_id = correlation_id if correlation_id is not None else uuid.uuid4()

    return {
        "Verb": verb,
        "Noun": "DERGroups",
        "Timestamp": datetime.datetime.now(),
        "MessageID": message_id,
        "CorrelationID": correlation_id
    }


def __build_der_function(connectDisconnect=True, frequencyWattCurveFunction=False, maxRealPowerLimiting=False,
                         rampRateControl=False, reactivePowerDispatch=False, voltageRegulation=False,
                         realPowerDispatch=True, voltVarCurveFunction=False, voltWattCurveFunction=False):
    return {
        "connectDisconnect": str(connectDisconnect).lower(),
        "frequencyWattCurveFunction": str(frequencyWattCurveFunction).lower(),
        "maxRealPowerLimiting": str(maxRealPowerLimiting).lower(),
        "rampRateControl": str(rampRateControl).lower(),
        "reactivePowerDispatch": str(reactivePowerDispatch).lower(),
        "voltageRegulation": str(voltageRegulation).lower(),
        "realPowerDispatch": str(realPowerDispatch).lower(),
        "voltVarCurveFunction": str(voltVarCurveFunction).lower(),
        "voltWattCurveFunction": str(voltWattCurveFunction).lower()
    }


def __build_enddevice_group(mrid, name, devices_mrid_list):
    return {
        "mRID": mrid,
        "description": name,
        "DERFunction": __build_der_function(),
        "EndDevices": devices_mrid_list,
        "Names": __build_names(name),
        "version": {
            "date": "2017-05-31T13:55:01-06:00",
            "major": 1,
            "minor": 0,
            "revision": 0
        }
    }


def __build_names(names):
    if not isinstance(names, list):
        names = [names]

    name_list = []
    for name in name_list:
        name_list.append({"name": name})
    return name_list


def __get_create_body(mrid, name, device_mrid_list):
    devices_mrid_list = [{"mRID": x} for x in device_mrid_list]
    body = {
        "DERGroups": [{
            "EndDeviceGroup": __build_enddevice_group(mrid, name, device_mrid_list)
        }]
    }
    return body


def create_group(mrid, name, device_mrid_list):
    history = HistoryPlugin()
    client = Client(c.CREATE_DERGROUP_ENDPOINT, plugins=[history])
    headers = __build_endpoint_header("create")
    body = __get_create_body(mrid, name, device_mrid_list)

    response = client.service.CreateDERGroups(Header=headers, Payload=body)
    _log.debug("Data Sent:\n{}".format(etree.tounicode(history.last_sent['envelope'], pretty_print=True)))
    #_log.debug("ZEEP Respons:\n{}".format(response))
    _log.debug("Data Response:\n{}".format(etree.tounicode(history.last_received['envelope'], pretty_print=True)))

    return response


def create_multiple_group(mrid_list, name_list, device_mrid_list_list):
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
    headers = __build_endpoint_header("delete")
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

    history = HistoryPlugin()
    client = Client(c.CHANGE_DERGROUP_ENDPOINT, plugins=[history])
    # node = client.create_message(client.service, 'CreateDERGroups', Header=headers, Payload=body)
    # print(node)

    response = client.service.DeleteDERGroups(Header=headers, Payload=body)
    _log.debug("Data Sent:\n{}".format(etree.tounicode(history.last_sent['envelope'], pretty_print=True)))
    # _log.debug("ZEEP Respons:\n{}".format(response))
    _log.debug("Data Response:\n{}".format(etree.tounicode(history.last_received['envelope'], pretty_print=True)))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    from derms_app.createDeviceJsonConf import Device

    # dev_list = [Device(uuid.uuid4(), "foo", "atype"),
    #             Device(uuid.uuid4(), "bar", "atype"),
    #             Device(uuid.uuid4(), "bim", "atype")]
    # create_group(uuid.uuid4(), "a group", dev_list)

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
    delete_group(mrid=uuid.uuid4())
#    delete_group("DG1")