import json
from copy import deepcopy

from derms_app import createDeviceJsonConf

devices = []


def get_devices():
    if not devices:
        for device in createDeviceJsonConf.getDeviceSubset():
            devices.append(device)

    return devices


def get_devices_json():
    lst = get_devices()
    return json.dumps([x.__dict__ for x in lst], indent=2)


if __name__ == '__main__':
    devices = get_devices()
    for x in devices:
        print(x.__dict__)

    print(get_devices_json())
