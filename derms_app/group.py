import json
import os
from threading import Lock

__groups = []

write_lock = Lock()


class Group:
    def __init__(self, mrid, name, deviceList):
        self.mrid = mrid
        self.name = name
        self.devices = deviceList


def get_groups_json():
    if not __groups:
        load_groups()
    return json.dumps([x.__dict__ for x in __groups])


def get_groups():
    if not __groups:
        load_groups()

    return __groups


def add_group(group_mrid, group_name, device_mrids):
    __groups.append(Group(group_mrid, group_name, device_mrids))
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
                __groups = json.loads(fp.read())
