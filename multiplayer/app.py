from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from components import *
import network
import json
import copy

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

def fetch_player(id):
    player = next((x for x in machines if hasattr(x, 'session_id') and x.session_id == request.sid), None)
    return player

def update_world():
    resolved_machines = network.resolve_network(machines)
    world_state = {'machines': [], 'connections': [], 'pool': []}

    for machine in resolved_machines:
        machine_json = copy.deepcopy(machine).__dict__

        # this is disgusting. rasmus if you are reading this I'm sorry.
        if hasattr(machine, 'outflow'):
            for i, outflow in enumerate(machine.outflow):
                if outflow is not False:
                    print('machine out is', outflow)
                    machine_json['outflow'][i] = {'amount': outflow['amount'], 'material': outflow['material'].__dict__}

        # again i am filled with remorse
        if hasattr(machine, 'inputs'):
            for i, machine_in in enumerate(machine.inputs):
                if machine_in is not False:
                    print('machine in is', machine_in)
                    machine_json['inputs'][i] = {'amount': machine_in['amount'], 'material': machine_in['material'].__dict__}

        # screaming, crying, throwing up
        if hasattr(machine, 'recipes'): del machine_json['recipes']

        if hasattr(machine, 'pool'):
            # move the pool to its own thing
            del machine_json['pool']

            for material_type in machine.pool:
                if material_type is not False:
                    world_state['pool'].append({'amount': material_type['amount'], 'material': material_type['material'].__dict__})

        world_state['machines'].append(machine_json)


    for connection in connections:
        world_state['connections'].append(connection.__dict__)

    emit('world_state', {'data': json.dumps(world_state)}, broadcast=True)

def initialise_grid():
    machines.append(inlet(str(network.machine_num()), 'inlet'))
    output = outlet(str(network.machine_num()), 'outlet')
    machines.append(output) 

def background_thread():
    # each tick, recalculate and send world state
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'another tick', 'count': count})

def remove_player(player_id):
    rm_player = fetch_player(player_id)
    if rm_player is not None: 
        machines.remove(rm_player)
        print('removed core', rm_player.machine_id)

def game_over(player_id):
    remove_player(player_id)
    emit('die')
    disconnect(player_id)

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.event
def create_core():
    # global machines
    session['receive_count'] = session.get('receive_count', 0) + 1
    new_core = core(str(network.machine_num()), request.sid, 'you', initial_energy=300)
    machines.append(new_core)
    print('created core', new_core.machine_id)
    emit('core_info',
         {'data': json.dumps(new_core.__dict__)})
    update_world()


@socketio.event
def connect():
    global thread
    print('server')
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

@socketio.event
def add_machine(data):
    global machines
    print('adding machine', data, request.sid)
    player = fetch_player(request.sid)
    machines, player = network.add_machine(data['machine_type'], machines, player)
    if not player.alive:
        game_over(player.session_id)
    print('machines is now', machines)
    update_world()

@socketio.event
def add_connection(conn_data):
    global machines, connections
    print('adding connection', json.dumps(conn_data), request.sid)
    player = fetch_player(request.sid)
    machines, connections, player = network.add_connection(conn_data['source'], conn_data['dest'], machines, connections, player)
    update_world()

@socketio.event
def rm_connection(conn_id):
    print('removing connection', conn_id, request.sid)
    update_world()

@socketio.event
def vote(conn_id):
    print('voting', conn_id, request.sid)

@socketio.event
def chat(message):
    emit('chat_msg', {'data': message['data']}, broadcast=True)

@socketio.on('disconnect')
def test_disconnect():
    remove_player(request.sid)

if __name__ == '__main__':
    initialise_grid()
    socketio.run(app)
