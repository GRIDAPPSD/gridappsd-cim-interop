from multiprocessing import Process
from threading import Lock
from time import sleep
from urllib.error import URLError

from flask import Flask, send_from_directory, request, render_template, make_response, redirect, url_for

from derms_app import createDeviceJsonConf
from derms_app import group, derms_client
# from derms_app.devices import get_devices_json, get_devices
from derms_app.device import get_devices_json
import json, jsons

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
__proc__ = None

deviceList = []
groupList = []
groupListByName = {}
groupListBymRID = {}

#groups =

@app.route('/')
def root():
    return app.send_static_file('index.html')


#@app.route('/static/<path:path>')
#def send_static_html(path):
#    return send_from_directory('static', path)

def json_response(content):
    response = make_response(content)
    response.headers['Content-Type'] = "application/json"
    return response


@app.route("/api/devices")
def device_list():
    return json_response(get_devices_json())


@app.route("/api/derm_groups")
def device_group_list():
    return json_response(group.get_groups_json())


@app.route("/api/device_groups/create", methods=["POST"])
def device_group_create(group_mrid, group_name, device_mrid_list):
    derms_response = derms_client.create_group(group_mrid, group_name, device_mrid_list)
    return json_response(derms_response)


write_lock = Lock()


@app.route("/api/delete_group/mrid/<mrid>")
def delete_group_mrid(mrid):
    return delete_group(mrid=mrid)


@app.route("/api/delete_group/name/<name>")
def delete_group_name(name):
    return delete_group(name=name)


def delete_group(mrid=None, name=None):
    # name = request.args.get("name")
    # mrid = request.args.get("mrid")

    assert name or mrid, "Name or mrid must be specified~"
    if mrid:
        response = derms_client.delete_group(mrid=mrid)
        if response.Reply.Result == "OK":
            pass
            # group.delete_group(group_mrid=mrid)
        else:
            return render_template('failedGroup-template.html', group=group.get_group_mrid(mrid), message='delete')
    else:
        response = derms_client.delete_group(name=name)
        if response.Reply.Result == "OK":
            pass
            # group.delete_group(group_name=name)
        else:
            return render_template('failedGroup-template.html', group=group.get_group_name(name), message='delete')
    return redirect("/list_groups")


@app.route("/create_group", methods=['POST', 'GET'])
def create_group_html():
    '''
    if form does not exist yet, show the create_group.html page
    if form exists, pull user input from the forms and create groups by calling function in derms_client
    :return:
    '''
    if request.method == 'POST':
        number_of_groups = int(request.form.get('number_of_groups'))
        group_list = []
        mrid_list = []
        name_list = []
        device_mrid_list_list = []
        for g_count in range(number_of_groups):
            group_mrid = request.form.get('group_mrid_' + str(g_count + 1))
            group_name = request.form.get('group_name_' + str(g_count + 1))
            group_description = request.form.get('group_description_' + str(g_count + 1))
            selected_devices = request.form.getlist('selected_devices_' + str(g_count + 1))

            # sort out form content by group, then need to call create_groups function in derms_client
            # this way, if create groups return successfully, we can add these groups directly to the groups list
            group_list.append(group.Group(group_mrid, group_name, group_description, selected_devices))

            # sort out form content to three lists, then call create_multiple_group function in derms_client
            # this way, we need to re-group the lists to groups in order to add them to the groups list
            # mrid_list.append(group_mrid)
            # name_list.append(group_name)
            # device_mrid_list_list.append(selected_devices)
        # if False:
        #     response = derms_client.create_group(group_mrid, group_name, selected_devices)
        # else:
        response = derms_client.create_groups(group_list)
        # response = derms_client.create_multiple_group(mrid_list, name_list, device_mrid_list_list)
        if response.Reply.Result == "OK":
            # group.add_group(group_mrid, group_name, selected_devices)
            group.add_groups(group_list)
            return redirect(url_for("list_group_html", status="Group created successfully!"))
        else:
            # return render_template("create-group.html", devices=get_devices(), group_mrid=group_mrid,
            #                        group_name=group_name, selected_devices=selected_devices,
            #                        status=response.Reply.Error)
            global deviceList
            if len(deviceList) == 0:
                deviceList = derms_client.get_devices()
                devices = deviceList
            else:
                devices = deviceList
            group_list.__len__()
            # return render_template("create-group.html", devices=devices, status=response.Reply.Error, groups=group_list, oldform=request.form)
            return render_template("create-group.html", devices=devices, status=response.Reply.Error)
    try:
        if len(deviceList) == 0:
            deviceList = derms_client.get_devices()
            devices = deviceList
        else:
            devices = deviceList
    except (URLError, ConnectionRefusedError) as e:
        return render_template("create-group.html", status="Blazegraph could not be found.")

    return render_template("create-group.html", devices=devices)


def _sortGroups(derGroups):
    groupList.clear()
    groupListByName.clear()
    groupListBymRID.clear()
    for g in derGroups:
        devices = []
        for d in g.EndDevices:
            devices.append(d.mRID)
        this_group = group.Group(g.mRID, g.Names[0].name, g.description, devices)
        groupList.append(this_group)
        groupListByName[g.description] = this_group
        groupListBymRID[g.mRID] = this_group


@app.route("/list_groups")
def list_group_html():
    '''
    List all created groups.
    '''
    try:
        derGroups = derms_client.get_end_device_groups()
        _sortGroups(derGroups)
        return render_template("list-groups.html", groups=derGroups, status=request.args.get('status'))
    except Exception as ex:
        return f'Error Getting DER Groups. <br />{str(ex)}'


@app.route("/list_devices")
def list_devices():
    try:
        global deviceList
        if len(deviceList) == 0:
            deviceList = derms_client.get_devices()
        return render_template("list-device-template.html", devices=deviceList)
    except Exception as ex:
        return f'Error Getting Devices.<br />{str(ex)}'
        # return 'Error Getting Devices.\n{}'.format(str(ex))
    # s = response[0]
    # so = response[1]
    # b = response[2]
    # a = 0
    # if response.Reply.Result == "OK":
    #     return "devices listed"
    # else:
    #     return "failed getting devices"


@app.route("/edit_group")
def edit_group():
    if not groupList:
        derGroups = derms_client.get_end_device_groups()
        _sortGroups(derGroups)
    return render_template("modify-groups-template.html", names=jsons.dump(groupListByName), mRIDs=groupListBymRID, groups=groupList)


# @app.route('/create')
# def createDeviceList():
#     a = createDeviceJsonConf.getDeviceSubset()
#     for dev in a:
#         deviceList.append(dev)
#     assert isinstance(deviceList, list)
#     return render_template('devices-template.html', devices=deviceList, mrid=uuid.uuid4())


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/api/create', methods=['POST'])
def create_group():
    groupName = request.form['groupName']
    groupmrid = request.form['mrid']
    devices = request.form.getlist('devices')
    thisDevices = []
    for dev in devices:
        devParts = dev.split(',')
        deviceName = devParts[0].strip(" ,()'")
        deviceType = devParts[1].strip(" ,()'")
        devicemrid = devParts[2].strip(" ,()'")
        newDevice = createDeviceJsonConf.Device(devicemrid, deviceName, deviceType)
        thisDevices.append(newDevice)

    newGroup = group.Group(groupmrid, groupName, thisDevices)

    # Build an xml structure to send to openderms
    # use zeep to send that xml structure to openderms/test instance and get response

    #success = zeep.createGroupCall()
    # if group created successfully
    if True:
        groupList.append(newGroup)
        return render_template('groupDetail-template.html', group=newGroup, message='created')
    else:
        return render_template('failedGroup-template.html', group=newGroup, message='create')

@app.route('/modify')
def modifyAGroup():
    return render_template('groups-template.html', groups=groupList)

@app.route('/api/edit', methods=['POST'])
def editGroup():
    group = request.form['groups']
    dgmrid = group.split(',')[1].strip(" ,()'")
    for grp in groupList:
        if grp.mrid == dgmrid:
            if request.form['action'] == 'Delete':
                return deleteGroup(grp)
            elif request.form['action'] == 'Modify':
                return render_template('devices-template.html', devices=deviceList, mrid=grp.mrid, groupname=grp.name)

            # if False:
            #     groupList.remove(grp)
            #     return render_template('groupDetail-template.html', group=grp, message='deleted')
            # else:
            #     return render_template('failedGroup-template.html', group=grp, message='delete')


# @app.route('/confirmation', methods=['POST'])
# def printMesasge():
#     # Build an xml structure to send to openderms
#     # use zeep to send that xml structure to openderms/test instance and get response
#
#     testName = request.form['textName']
#     print('testName: ' + testName)
#     message = request.form['message']
#     print('message: ' + message)
#     return "meesage sent."


def deleteGroup(group):
    # success = zeep.deleteGroupCall()
    if True:
        groupList.remove(group)
        return render_template('groupDetail-template.html', group=group, message='deleted')
    else:
        return render_template('failedGroup-template.html', group=group, message='delete')


def get_app():
    return app


def start_server_proc():
    global __proc__
    __proc__ = Process(target=__start_app__)
    __proc__.daemon = True
    __proc__.start()


def __start_app__():
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.run(port=8442, debug=True)


if __name__ == '__main__':
    start_server_proc()
    while True:
        sleep(0.1)
