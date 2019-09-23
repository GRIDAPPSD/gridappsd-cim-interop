from flask import Flask, send_from_directory, request, render_template
from multiprocessing import Process
from time import sleep
import json
import uuid

from derms_app import createDeviceJsonConf
from derms_app import group


# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
__proc__ = None

deviceList = []
groupList = []


@app.route('/')
def root():
    return app.send_static_file('index.html')


#@app.route('/static/<path:path>')
#def send_static_html(path):
#    return send_from_directory('static', path)


@app.route('/create')
def createDeviceList():
    a = createDeviceJsonConf.getDeviceSubset()
    for dev in a:
        deviceList.append(dev)
    assert isinstance(deviceList, list)
    return render_template('devices-template.html', devices=deviceList, mrid=uuid.uuid4())

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

def deleteGroup(group):
    # success = zeep.deleteGroupCall()
    if True:
        groupList.remove(group)
        return render_template('groupDetail-template.html', group=group, message='deleted')
    else:
        return render_template('failedGroup-template.html', group=group, message='delete')


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


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


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
