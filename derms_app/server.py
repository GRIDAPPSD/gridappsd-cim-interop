from flask import Flask, send_from_directory, request
from multiprocessing import Process
from time import sleep

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
__proc__ = None


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/static/<path:path>')
def send_static_html(path):
    return send_from_directory('static', path)


@app.route('/api/create')
def create_group():
    # Build an xml structure to send to openderms
    # use zeep to send that xml structure to openderms/test instance and get response
    pass


@app.route('/confirmation', methods=['POST'])
def printMesasge():
    # Build an xml structure to send to openderms
    # use zeep to send that xml structure to openderms/test instance and get response

    testName = request.form['textName']
    print('testName: ' + testName)
    message = request.form['message']
    print('message: ' + message)
    return "meesage sent."


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
