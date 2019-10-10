import json
import os
from threading import Lock

__groups = {}

write_lock = Lock()


class Group:
    def __init__(self, mrid, name, deviceList):
        self.mrid = mrid
        self.name = name
        self.devices = deviceList


def get_groups_json():
    if not __groups:
        load_groups()
    json_dict = {}
    for k, v in __groups.items():
        json_dict[k] = v.__dict__
    return json.dumps(json_dict)


def get_groups():
    if not __groups:
        load_groups()

    return __groups


def get_group_mrid(mrid):
    if not __groups:
        load_groups()

    return __groups[mrid]


def get_group_name(name):
    if not __groups:
        load_groups()
    groups_by_name = {y.name:y for x,y in __groups.iteritems()}
    return groups_by_name[name]


def add_group(group_mrid, group_name, device_mrids):
    __groups[group_mrid] = Group(group_mrid, group_name, device_mrids)
    with write_lock:
        save_groups()


def delete_group(group_mrid=None, group_name=None):
    assert group_mrid or group_name, "must specify either group name or group mrid"
    assert not (group_mrid and group_name), "must specify either group name or group mrid"
    found_mrid = None
    if group_mrid:
        found_mrid = group_mrid
    else:
        for k, v in __groups.items():
            if v.name == group_name:
                found_mrid = k
                break

    del __groups[group_mrid]
    with write_lock:
        save_groups()


def save_groups():
    file = "groups.json"
    if not __groups:
        json_dump = get_groups_json()

        with open(file, "w") as fp:
            fp.write(json_dump)


def load_groups():
    global __groups

    file = "groups.json"
    if os.path.exists(file):
        with open(file, "r") as fp:
            data = fp.read()
            if data:
                __groups = json.loads(data)
