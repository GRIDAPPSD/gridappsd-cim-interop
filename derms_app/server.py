from flask import Flask, send_from_directory, request, render_template, make_response, redirect
from threading import Lock
from multiprocessing import Process
from time import sleep
import json
import uuid
from urllib.error import URLError

from derms_app import group, derms_client
from derms_app.devices import get_devices_json, get_devices

from flask_restful import Resource, Api


# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
__proc__ = None

deviceList = []
groupList = []

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
            group.delete_group(group_mrid=mrid)
        else:
            return render_template('failedGroup-template.html', group=group.get_group_mrid(mrid), message='delete')
    else:
        response = derms_client.delete_group(name=name)
        if response.Reply.Result == "OK":
            group.delete_group(group_name=name)
        else:
            return render_template('failedGroup-template.html', group=group.get_group_name(name), message='delete')
    return redirect("/list_groups")


@app.route("/create_group", methods=['POST', 'GET'])
def create_group_html():
    if request.method == 'POST':
        number_of_groups = int(request.form.get('number_of_groups'))
        group_list = []
        for g_count in range(number_of_groups):
            group_mrid = request.form.get('group_mrid_' + str(g_count + 1))
            group_name = request.form.get('group_name_' + str(g_count + 1))
            selected_devices = request.form.getlist('selected_devices_' + str(g_count + 1))
            group_list.append(group.Group(group_mrid, group_name, selected_devices))
        if False:
            response = derms_client.create_group(group_mrid, group_name, selected_devices)
        else:
            response = derms_client.create_groups(group_list)
        if response.Reply.Result == "OK":
            # group.add_group(group_mrid, group_name, selected_devices)
            group.add_groups(group_list)
            return redirect("/list_groups")
        else:
            return render_template("create-group.html", devices=get_devices(), group_mrid=group_mrid,
                                   group_name=group_name, selected_devices=selected_devices,
                                   status=response.Reply.Error)
    try:
        devices = get_devices()
    except (URLError, ConnectionRefusedError) as e:
        return render_template("create-group.html", status="Blazegraph could not be found.")

    return render_template("create-group.html", devices=get_devices())


@app.route("/list_groups")
def list_group_html():
    return render_template("list-groups.html", groups=group.get_groups())


@app.route('/create')
def createDeviceList():
    a = createDeviceJsonConf.getDeviceSubset()
    for dev in a:
        deviceList.append(dev)
    assert isinstance(deviceList, list)
    return render_template('devices-template.html', devices=deviceList, mrid=uuid.uuid4())


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
    app.run(port=8443, debug=True)


if __name__ == '__main__':
    start_server_proc()
    while True:
        sleep(0.1)
