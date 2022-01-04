from multiprocessing import Process
from threading import Lock
from time import sleep
from urllib.error import URLError

from flask import Flask, send_from_directory, request, render_template, make_response, redirect, url_for, Response

# from derms_app import createDeviceJsonConf
from derms_app import group, derms_client
# from derms_app.devices import get_devices_json, get_devices
from derms_app.device import Device, get_devices
import json, jsons
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader


# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
__proc__ = None

deviceList = []
groupList = []
groupListByName = {}
groupListBymRID = {}

simulation_id = 0
model_namelist = ['acep_psil', 'final9500node', 'ieee123pv', 'ieee13nodeckt', 'j1', 'test9500new', 'ieee123']
model_mridlist = ['_77966920-E1EC-EE8A-23EE-4EFD23B205BD', '_EE71F6C9-56F0-4167-A14E-7F4C71F10EAA',
                  '_E407CBB6-8C8D-9BC9-589C-AB83FBF0826D', '_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62',
                  '_67AB291F-DCCD-31B7-B499-338206B9828F', '_AAE94E4A-2465-6F5E-37B1-3E72183A4E44',
                  '_C1C3E687-6FFD-C753-582B-632A27E28507', ]
model_name = None
model_mrid = None


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/menu', methods=['GET', 'POST'])
def target_chosen():
    if request.method == 'POST':
        target = request.form['target']
        # from derms_app import constants as c
        if target == 'epri':
            derms_client.c.USE_SIMULATOR_FOR_SOAP = True
            # derms_client.c.re_import()
            from epri_simulator import (CREATE_NAMESPACE_SOAP_BINDING, CHANGE_NAMESPACE_SOAP_BINDING,
                                          CREATE_DERGROUP_ENDPOINT, CHANGE_DERGROUP_ENDPOINT,
                                          QUERY_DERGROUP_ENDPOINT, QUERY_NAMESPACE_SOAP_BINDING,
                                        QUERY_NAMESPACE_STATUS_SOAP_BINDING, QUERY_DERGROUP_STATUS_ENDPOINT)
            derms_client.c.CHANGE_NAMESPACE_SOAP_BINDING = CHANGE_NAMESPACE_SOAP_BINDING
            derms_client.c.CREATE_NAMESPACE_SOAP_BINDING = CREATE_NAMESPACE_SOAP_BINDING
            derms_client.c.CREATE_DERGROUP_ENDPOINT = CREATE_DERGROUP_ENDPOINT
            derms_client.c.CHANGE_DERGROUP_ENDPOINT = CHANGE_DERGROUP_ENDPOINT
            derms_client.c.QUERY_DERGROUP_ENDPOINT = QUERY_DERGROUP_ENDPOINT
            derms_client.c.QUERY_NAMESPACE_SOAP_BINDING = QUERY_NAMESPACE_SOAP_BINDING
            derms_client.c.QUERY_NAMESPACE_STATUS_SOAP_BINDING = QUERY_NAMESPACE_STATUS_SOAP_BINDING
            derms_client.c.QUERY_DERGROUP_STATUS_ENDPOINT = QUERY_DERGROUP_STATUS_ENDPOINT
            derms_client.c.SOAP_BINDINGS = dict(
                CREATE=CREATE_NAMESPACE_SOAP_BINDING,
                # Both delete and change use the same binding
                DELETE=CHANGE_NAMESPACE_SOAP_BINDING,
                CHANGE=CHANGE_NAMESPACE_SOAP_BINDING,
                GET=QUERY_NAMESPACE_SOAP_BINDING
            )
            derms_client.c.STATUS_SOAP_BINDINGS = dict(
                CREATE=CREATE_NAMESPACE_SOAP_BINDING,
                # Both delete and change use the same binding
                DELETE=CHANGE_NAMESPACE_SOAP_BINDING,
                CHANGE=CHANGE_NAMESPACE_SOAP_BINDING,
                GET=QUERY_NAMESPACE_STATUS_SOAP_BINDING
            )
        else:
            derms_client.c.USE_SIMULATOR_FOR_SOAP = False
    return app.send_static_file('menu.html')
    # return app.send_static_file('index.html')

#@app.route('/static/<path:path>')
#def send_static_html(path):
#    return send_from_directory('static', path)

def json_response(content):
    response = make_response(content)
    response.headers['Content-Type'] = "application/json"
    return response


@app.route("/api/devices")
def device_list():
    pass
    # return json_response(get_devices_json())


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
    return _delete_group(mrid=mrid)


@app.route("/api/delete_group/name/<name>")
def delete_group_name(name):
    return _delete_group(name=name)


def _delete_group(mrid=None, name=None):
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


@app.route("/delete_group/<group>")
def delete_group(group):
    print(group)
    if group in groupListBymRID:
        return _delete_group(mrid=group)
    else:
        return _delete_group(name=group)


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
        for g_count in range(number_of_groups):
            group_mrid = request.form.get('group_mrid_' + str(g_count + 1))
            group_name = request.form.get('group_name_' + str(g_count + 1))
            group_description = request.form.get('group_description_' + str(g_count + 1))
            selected_devices = request.form.getlist('selected_devices_' + str(g_count + 1))

            derFunctions = group.DERFunctions()
            derFunctions.connectDisconnect = request.form.get('connectDisconnect_' + str(g_count + 1)) is not None
            derFunctions.frequencyWattCurveFunction = request.form.get('frequencyWattCurveFunction_' + str(g_count + 1)) is not None
            derFunctions.maxRealPowerLimiting = request.form.get('maxRealPowerLimiting_' + str(g_count + 1)) is not None
            derFunctions.rampRateControl = request.form.get('rampRateControl_' + str(g_count + 1)) != None
            derFunctions.reactivePowerDispatch = request.form.get('reactivePowerDispatch_' + str(g_count + 1)) != None
            derFunctions.realPowerDispatch = request.form.get('realPowerDispatch_' + str(g_count + 1)) != None
            derFunctions.voltageRegulation = request.form.get('voltageRegulation_' + str(g_count + 1)) != None
            derFunctions.voltVarCurveFunction = request.form.get('voltVarCurveFunction_' + str(g_count + 1)) != None
            derFunctions.voltWattCurveFunction = request.form.get('voltWattCurveFunction_' + str(g_count + 1)) != None

            # sort out form content by group, then need to call create_groups function in derms_client
            # this way, if create groups return successfully, we can add these groups directly to the groups list
            group_list.append(group.Group(group_mrid, group_name, group_description, selected_devices, derFunctions))

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
                deviceList = derms_client.get_devices(model_mrid)
                devices = deviceList
            else:
                devices = deviceList
            group_list.__len__()
            # return render_template("create-group.html", devices=devices, status=response.Reply.Error, groups=group_list, oldform=request.form)
            return render_template("create-group.html", devices=devices, status=response.Reply.Error)
    try:
        if len(deviceList) == 0:
            try:
                deviceList = derms_client.get_devices(model_mrid)
            except Exception as e:
                deviceList = get_devices()
            devices = deviceList
        else:
            devices = deviceList
    except (URLError, ConnectionRefusedError) as e:
        return render_template("create-group.html", status="Blazegraph could not be found.")

    return render_template("create-group.html", devices=devices)


@app.route("/retrieve_groups")
def retrieve_groups_html():
    if not groupList:
        response = derms_client.query_all_groups()
        _sortGroups(response.Payload.DERGroups.EndDeviceGroup)
    # return send_from_directory('static', 'retrieve-groups-template.html')
    return render_template('retrieve-groups-template.html', names=groupListByName, mRIDs=groupListBymRID)


@app.route("/query_group", methods=["POST"])
def query_groups():
    method = request.form.get('retrieveChoices')
    ngroup = request.form.get('ngroup')
    groupName = []
    groupMrid = []
    if method == "name":
        if ngroup == "oneGroup":
            groupName.append(request.form.get('queryid1'))
        else:
            groupName.append(request.form.get('queryid1'))
            groupName.append(request.form.get('queryid2'))
    else:
        if ngroup == "oneGroup":
            groupMrid.append(request.form.get('queryid1'))
        else:
            groupMrid.append(request.form.get('queryid1'))
            groupMrid.append(request.form.get('queryid2'))
    assert groupName or groupMrid
    assert not (groupName and groupMrid)
    if groupName:
        try:
            response = derms_client.query_groups_byName(groupName)
        except Exception as e:
            return "Query group by name failed.<br />" + str(e)
    elif groupMrid:
        try:
            response = derms_client.query_groups_bymRID(groupMrid)
        except Exception as e:
            return "Query group by mRID failed.<br />" + str(e)

    if response.Reply.Result == "OK":
        groups = []
        for g in response.Payload.DERGroups.EndDeviceGroup:
            devices = []
            for d in g.EndDevices:
                if d.Names:
                    dname = d.Names[0].name
                else:
                    dname = None
                devices.append(Device(mRID=d.mRID, name=dname))
            if g.Names:
                gname = g.Names[0].name
            else:
                gname = None
            if g.DERFunction != None:
                derfuncs={'connectDisconnect': g.DERFunction.connectDisconnect,
                             'frequencyWattCurveFunction': g.DERFunction.frequencyWattCurveFunction,
                             'maxRealPowerLimiting': g.DERFunction.maxRealPowerLimiting,
                             'rampRateControl': g.DERFunction.rampRateControl,
                             'reactivePowerDispatch': g.DERFunction.reactivePowerDispatch,
                             'realPowerDispatch': g.DERFunction.realPowerDispatch,
                             'voltageRegulation': g.DERFunction.voltageRegulation,
                             'voltVarCurveFunction': g.DERFunction.voltVarCurveFunction,
                             'voltWattCurveFunction': g.DERFunction.voltWattCurveFunction}
            if g.mRID:
                this_group = group.Group(g.mRID, gname, g.description, devices, derFunctions=derfuncs)
                groups.append(this_group)
        return render_template("list-groups.html", groups=groups, status="Group query returned successfully!",
                               query=True)
    else:
        return "Error query group"


def _sortGroups(derGroups):
    groupList.clear()
    groupListByName.clear()
    groupListBymRID.clear()
    for g in derGroups:
        devices = []
        for d in g.EndDevices:
            if d.Names:
                dname = d.Names[0].name
            else:
                dname = None
            devices.append(Device(mRID=d.mRID, name=dname))
        if g.Names:
            gname = g.Names[0].name
        else:
            gname = None
        if g.DERFunction != None:
            # derfuncs=group.DERFunctions(connectDisconnect=g.DERFunction.connectDisconnect,
            #              frequencyWattCurveFunction=g.DERFunction.frequencyWattCurveFunction,
            #              maxRealPowerLimiting=g.DERFunction.maxRealPowerLimiting,
            #              rampRateControl=g.DERFunction.rampRateControl,
            #              reactivePowerDispatch=g.DERFunction.reactivePowerDispatch,
            #              realPowerDispatch=g.DERFunction.realPowerDispatch,
            #              voltageRegulation=g.DERFunction.voltageRegulation,
            #              voltVarCurveFunction=g.DERFunction.voltVarCurveFunction,
            #              voltWattCurveFunction=g.DERFunction.voltWattCurveFunction)
            derfuncs={'connectDisconnect': g.DERFunction.connectDisconnect,
                         'frequencyWattCurveFunction': g.DERFunction.frequencyWattCurveFunction,
                         'maxRealPowerLimiting': g.DERFunction.maxRealPowerLimiting,
                         'rampRateControl': g.DERFunction.rampRateControl,
                         'reactivePowerDispatch': g.DERFunction.reactivePowerDispatch,
                         'realPowerDispatch': g.DERFunction.realPowerDispatch,
                         'voltageRegulation': g.DERFunction.voltageRegulation,
                         'voltVarCurveFunction': g.DERFunction.voltVarCurveFunction,
                         'voltWattCurveFunction': g.DERFunction.voltWattCurveFunction}
        if g.mRID:
            this_group = group.Group(g.mRID, gname, g.description, devices, derFunctions=derfuncs)
            groupList.append(this_group)
            groupListByName[gname] = this_group
            groupListBymRID[g.mRID] = this_group


@app.route("/list_groups")
def list_group_html():
    '''
    List all created groups.
    '''
    try:
        # derGroups = derms_client.get_end_device_groups()
        response = derms_client.query_all_groups()
        _sortGroups(response.Payload.DERGroups.EndDeviceGroup)
        return render_template("list-groups.html", groups=groupList, status=request.args.get('status'))
    except Exception as ex:
        return f'Error Query all DER Groups. <br />{str(ex)}'


@app.route("/load_model", methods=['POST', 'GET'])
def load_model():
    if request.method == 'POST':
        global model_name
        global model_mrid
        model_name = request.form.get('mymodel')
        if model_name in model_namelist:
            index = model_namelist.index(model_name)
            model_mrid = model_mridlist[index]
        else:
            model_mrid = None
    return render_template('load-model.html', exist_name=model_name, exist_mrid=model_mrid)


@app.route("/list_devices")
def list_devices():
    # try:
    global deviceList
    # if deviceList is None or len(deviceList) == 0:
    try:
        deviceList = derms_client.get_devices(model_mrid)
    except Exception as e:
        deviceList = get_devices()
        # with open("devices_list.json", "w") as fp:
        #     a = json.dumps([d.__json__() for d in deviceList])
        #     fp.write(a)
    if deviceList:
        return render_template("list-device-template.html", devices=deviceList)
    else:
        return f'Error Getting Devices.<br />'
    # except Exception as ex:
    #     return f'Error Getting Devices.<br />{str(ex)}'
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
        try:
            response = derms_client.query_all_groups()
            _sortGroups(response.Payload.DERGroups.EndDeviceGroup)
        except Exception as e:
            pass
        # derGroups = derms_client.get_end_device_groups()
        # _sortGroups(derGroups)
    global deviceList
    if len(deviceList) == 0:
        try:
            deviceList = derms_client.get_devices(model_mrid)
        except Exception as e:
            deviceList = get_devices()
    return render_template("modify-groups-template.html", names=groupListByName, mRIDs=groupListBymRID, groups=groupList, devices=deviceList)


@app.route("/run_simulation", methods=['GET', 'POST'])
def run_simulation():
    return render_template('run-simulation.html')


@app.route("/configuration", methods=['POST'])
def configuration():
    if request.method == 'POST':

        path = request.form.get('path')
        global simulation_id

        simulation_id, list_process_status = derms_client.run_simulation(path)
        return simulation_status()
        # return render_template("simulation-status.html", simu_id=str(simulation_id))


@app.route("/simulation_status", methods=['GET', 'POST'])
def simulation_status():
    def inner():
            length_old = 0
            while True:
                sleep(2)

                with open('message.log') as f:
                    lines = f.readlines()
                length = len(lines)
                message = lines[length_old:length]

                if length == length_old:
                    sleep(5)
                    with open('message.log') as f:
                        lines = f.readlines()
                    if len(lines) == length:
                        break
                else:
                    length_old = length
                    yield message

    env = Environment(loader=FileSystemLoader('templates'))
    tmpl = env.get_template('simulation-status.html')

    return Response(tmpl.generate(simu_id=str(simulation_id), messages=inner()))


# @app.route("/dispatch", methods=['GET', 'POST'])
# def dispath():
    #querry measurement ID
    #select one or multiple measuremnts
        #dispatch them
        #PNV_obj, VA_obj
            #querry p, q


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


# @app.route('/api/create', methods=['POST'])
# def create_group():
#     groupName = request.form['groupName']
#     groupmrid = request.form['mrid']
#     devices = request.form.getlist('devices')
#     thisDevices = []
#     for dev in devices:
#         devParts = dev.split(',')
#         deviceName = devParts[0].strip(" ,()'")
#         deviceType = devParts[1].strip(" ,()'")
#         devicemrid = devParts[2].strip(" ,()'")
#         newDevice = createDeviceJsonConf.Device(devicemrid, deviceName, deviceType)
#         thisDevices.append(newDevice)
#
#     newGroup = group.Group(groupmrid, groupName, thisDevices)
#
#     # Build an xml structure to send to openderms
#     # use zeep to send that xml structure to openderms/test instance and get response
#
#     #success = zeep.createGroupCall()
#     # if group created successfully
#     if True:
#         groupList.append(newGroup)
#         return render_template('groupDetail-template.html', group=newGroup, message='created')
#     else:
#         return render_template('failedGroup-template.html', group=newGroup, message='create')


@app.route('/modify', methods=['POST'])
def modifyAGroup():
    # agroup = request.args.get('agroup')
    # print(agroup)
    if request.method == 'POST':
        devices = request.form.getlist('selected_devices')
        groupBy = request.form.get('groupBy')
        groupChoices = request.form.get('groupChoices')
        if groupBy == "listGroupsByName":
            originalgroup = groupListByName[groupChoices]
        else:
            originalgroup = groupListBymRID[groupChoices]
        devicesl = []
        devicedict = {x.mRID: x for x in deviceList}
        for d in devices:
            devicesl.append(devicedict[d])

        derFunctions = group.DERFunctions()
        if request.form.get('connectDisconnect'):
            derFunctions.connectDisconnect = True
        else:
            derFunctions.connectDisconnect = False
        if request.form.get('frequencyWattCurveFunction'):
            derFunctions.frequencyWattCurveFunction = True
        else:
            derFunctions.frequencyWattCurveFunction = False
        if request.form.get('maxRealPowerLimiting'):
            derFunctions.maxRealPowerLimiting = True
        else:
            derFunctions.maxRealPowerLimiting = False
        if request.form.get('rampRateControl'):
            derFunctions.rampRateControl = True
        else:
            derFunctions.rampRateControl = False
        if request.form.get('reactivePowerDispatch'):
            derFunctions.reactivePowerDispatch = True
        else:
            derFunctions.reactivePowerDispatch = False
        if request.form.get('realPowerDispatch'):
            derFunctions.realPowerDispatch = True
        else:
            derFunctions.realPowerDispatch = False
        if request.form.get('voltageRegulation'):
            derFunctions.voltageRegulation = True
        else:
            derFunctions.voltageRegulation = False
        if request.form.get('voltVarCurveFunction'):
            derFunctions.voltVarCurveFunction = True
        else:
            derFunctions.voltVarCurveFunction = False
        if request.form.get('voltWattCurveFunction'):
            derFunctions.voltWattCurveFunction = True
        else:
            derFunctions.voltWattCurveFunction = False
        modifiedgroup = group.Group(originalgroup.mrid, originalgroup.name, originalgroup.description, devicesl, derFunctions)

        try:
            response = derms_client.modify_a_group(originalgroup, modifiedgroup)
        except Exception as e:
            return "Modify a group by name failed.<br />" + str(e)

        if response.Reply.Result == "OK":
            return render_template('groupDetail-template.html', group=modifiedgroup, message="modified")
        else:
            return "Modify a group failed.<br />" + str(response.Reply.Error)


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


@app.route('/get_group_status', methods=['GET', 'POST'])
def getGroupStatus():
    if request.method == 'POST':
        status = []
        select1 = request.form.get('group1')
        if select1:
            status.append(select1)
        select2 = request.form.get('group2')
        if select2:
            status.append(select2)
        if status:
            response = derms_client.query_group_status(status)
            return render_template("group-status-returned.html", status=status)
        else:
            return "please select at least one group to query."
        # if select1 and select2:
        #     status.append(select1)
        #     status.append(select2)
        #     response = derms_client.create_groups(status)
        #     return render_template("query-group-status.html", groups=groupList)
        # elif select1:
        #     status.append(select1)
        #     response = derms_client.create_groups(status)
        #     return "select1 to query."
        # elif select2:
        #     status.append(select2)
        #     response = derms_client.create_groups(status)
        #     return "select2 to query."
        # else:
        #     return "please select at least one group to query."
    else:
        if not groupList:
            # response = derms_client.query_all_groups()
            # _sortGroups(response.Payload.DERGroups.EndDeviceGroup)
            try:
                response = derms_client.query_all_groups()
                _sortGroups(response.Payload.DERGroups.EndDeviceGroup)
            except Exception as ex:
                pass
        return render_template("query-group-status.html", groups=groupList)


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
