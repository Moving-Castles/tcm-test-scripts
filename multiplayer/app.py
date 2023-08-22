from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from components import *
import network
import json

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
machines = []
connections = []
machine_number = 0

def initialise_grid():
    global machines
    machines.append(inlet(network.machine_num(), 'inlet'))
    output = outlet(network.machine_num(), 'outlet')
    machines.append(output)

    return machines, output  

def background_thread():
    # each tick, recalculate and send world state
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'another tick', 'count': count})


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.event
def create_core():
    # global machines
    session['receive_count'] = session.get('receive_count', 0) + 1
    new_core = core(network.machine_num(), request.sid, 'you', initial_energy=300)
    machines.append(new_core)
    print('created core', new_core.machine_id)
    emit('core_info',
         {'data': json.dumps(new_core.__dict__)})


@socketio.event
def connect():
    global thread
    print('server')
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.event
def add_machine(machine_type):
    print('adding machine', machine_type, request.sid)

@socketio.event
def add_connection(conn_data):
    print('adding connection', json.dumps(conn_data), request.sid)

@socketio.event
def rm_connection(conn_id):
    print('removing connection', conn_id, request.sid)

@socketio.event
def vote(conn_id):
    print('voting', conn_id, request.sid)

@socketio.on('disconnect')
def test_disconnect():
    rem_core = next((x for x in machines if hasattr(x, 'session_id') and x.session_id == request.sid), None)
    machines.remove(rem_core)
    print('removed core', rem_core.machine_id)


if __name__ == '__main__':
    initialise_grid()
    socketio.run(app)
