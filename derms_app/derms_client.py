import datetime
import logging
from lxml import etree
import uuid

from zeep import Client
from zeep.plugins import HistoryPlugin

from derms_app import constants as c

_log = logging.getLogger(__name__)


def __get_create_headers(verb, message_id=None, correlation_id=None):
    message_id = message_id if message_id is not None else uuid.uuid4()
    correlation_id = correlation_id if correlation_id is not None else uuid.uuid4()

    return {
        "Verb": verb,
        "Noun": "DERGroups",
        "Timestamp": datetime.datetime.now(),
        "MessageID": message_id,
        "CorrelationID": correlation_id
    }


def __get_create_body(mrid, name, device_mrid_list):
    devices_mrid_list = [{"mRID": x} for x in device_mrid_list]
    body = {
            "DERGroups": {
                "EndDeviceGroup": {
                    "mRID": mrid,
                    "description": "DER Group 1",
                    "DERFunction": {
                        "connectDisconnect": "true",
                        "frequencyWattCurveFunction": "false",
                        "maxRealPowerLimiting": "false",
                        "rampRateControl": "false",
                        "reactivePowerDispatch": "false",
                        "realPowerDispatch": "true",
                        "voltageRegulation": "false",
                        "voltVarCurveFunction": "false",
                        "voltWattCurveFunction": "false"
                    },
                    "EndDevices": devices_mrid_list,
                    "Names": [
                        {"name": name}
                    ],
                    "version": {
                        "date": "2017-05-31T13:55:01-06:00",
                        "major": 1,
                        "minor": 0,
                        "revision": 0
                    }
                }

            }
        }
    return body


def create_group(mrid, name, device_mrid_list):
    history = HistoryPlugin()
    client = Client(c.CREATE_DERMS_ENDPOINT, plugins=[history])
    headers = __get_create_headers("create")
    body = __get_create_body(mrid, name, device_mrid_list)

    response = client.service.CreateDERGroups(Header=headers, Payload=body)
    _log.debug("Data Sent:\n{}".format(etree.tounicode(history.last_sent['envelope'], pretty_print=True)))
    _log.debug("ZEEP Respons:\n{}".format(response))
    # _log.debug("Data Response:\n{}".format(etree.tounicode(history.last_received['envelope'], pretty_print=True)))

    return response


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    from derms_app.createDeviceJsonConf import Device
    dev_list = [Device(uuid.uuid4(), "foo", "atype"),
                Device(uuid.uuid4(), "bar", "atype"),
                Device(uuid.uuid4(), "bim", "atype")]
    create_group(uuid.uuid4(), "a group", dev_list)