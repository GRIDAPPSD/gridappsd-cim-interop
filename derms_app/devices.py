# import json
# from copy import deepcopy
#
# # from derms_app import createDeviceJsonConf
#
# class Device:
#     '''
#     class represent a device/electronics
#     '''
#     def __init__(self, mrid, name, type):
#         self.mrid = mrid
#         self.name = name
#         self.type = type
#
#     def __json__(self):
#         return json.dumps({"mrid": self.mrid,
#                            "name": self.name,
#                            "type": self.type})
#
#     def tojson(self):
#         return self.__json__()
#
#
# devices = []
#
#
# # def get_devices():
# #     with open("devices_list.json") as fp:
# #         loaded_json = json.loads(fp.read())
# #
# #     devices_list = []
# #
# #     for x in loaded_json['devices']:
# #         devices_list.append(Device(x['mrid'], x['name'], "ADevice"))
# #
# #     if not devices:
# #         for device in devices_list:
# #             devices.append(device)
# #
# #     return devices
#
#
# # def get_devices_json():
# #     lst = get_devices()
# #     return json.dumps([x.__dict__ for x in lst], indent=2)
#
#
# # if __name__ == '__main__':
#     # devices = get_devices()
#     # for x in devices:
#     #     print(x.__dict__)
#     #
#     # print(get_devices_json())
