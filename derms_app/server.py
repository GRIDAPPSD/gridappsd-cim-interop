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

groupList = []

@app.route('/')
def root():
    return app.send_static_file('index.html')


#@app.route('/static/<path:path>')
#def send_static_html(path):
#    return send_from_directory('static', path)


@app.route('/create')
def createDeviceList():
    deviceList = createDeviceJsonConf.getDeviceSubset()
    assert isinstance(deviceList, list)
    return render_template('devices-template.html', devices=deviceList, mrid=uuid.uuid4())

@app.route('/api/create', methods=['POST'])
def create_group():
    groupName = request.form['groupName']
    groupmrid = request.form['mrid']
    devices = request.form.getlist('devices')
    devicesList = []
    for dev in devices:
        devParts = dev.split(',')
        deviceName = devParts[0].strip(" ,()'")
        deviceType = devParts[1].strip(" ,()'")
        devicemrid = devParts[2].strip(" ,()'")
        newDevice = createDeviceJsonConf.Device(devicemrid, deviceName, deviceType)
        devicesList.append(newDevice)

    newGroup = group.Group(groupmrid, groupName, devicesList)

    # Build an xml structure to send to openderms
    # use zeep to send that xml structure to openderms/test instance and get response

    #success = zeep.createGroupCall()
    # if group created successfully
    if False:
        groupList.append(newGroup)
        return render_template('groupDetail-template.html', group=newGroup, message='created')
    else:
        return render_template('failedGroup-template.html', group=newGroup, message='create')


@app.route('/delete')
def deleteAGroup():
    return render_template('groups-template.html', groups=groupList)

@app.route('/api/delete', methods=['POST'])
def delete_group():
    group = request.form['groups']
    dgmrid = group.split(',')[1].strip(" ,()'")
    for grp in groupList:
        if grp.mrid == dgmrid:
            # success = zeep.deleteGroupCall()
            if False:
                groupList.remove(grp)
                return render_template('groupDetail-template.html', group=grp, message='deleted')
            else:
                return render_template('failedGroup-template.html', group=grp, message='delete')

    return "success"


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
