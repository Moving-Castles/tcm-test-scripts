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
async_mode = "eventlet"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
machines = []
connections = []
machine_number = 0
connection_number = 0
energy_delta = 1
win_state = [{
    'material_name': 'concrete',
    'amount': 10,
    'done': False
}]

def log_event(event):
    print('logging', event)
    socketio.emit('log_event', {'data': event})

def victory(context='main'):
    if context=='main': emit('victory', broadcast=True)
    else: socketio.emit('victory')

    log_event('the box has been won')

def game_over(player, context='main'):
    player_id = player.session_id
    remove_player(player_id)
    if context=='main':
        emit('die')
        disconnect(player_id)
    else: 
        socketio.emit('die', to=player_id)   
        disconnect(player_id, namespace='/')

    log_event('core ' + player.machine_id + ' has died :(')

def check_win_state(world_state, context='main'):
    global win_state

    for win_material in win_state:
        pool_material = next((o for o in world_state['pool'] if o['material']['name'] == win_material['material_name']), None)
        if pool_material is not None:
            if pool_material['amount'] >= win_material['amount']:
                log_event('you got enough ' + win_material['material_name'] + '!')
                win_state.remove(win_material)

    if len(win_state) == 0:
        victory(context)


def status_message(message, player_id, context='main'):
    if context=='main': emit('status_message', {'data': message }, to=player_id, namespace='/')
    else: socketio.emit('status_message', {'data': message }, to=player_id, namespace='/')


def feedback_message(message, player_id, context='main'):
    if context=='main': emit('feedback_message', {'data': message }, to=player_id, namespace='/')
    else: socketio.emit('feedback_message', {'data': message }, to=player_id, namespace='/')

def fetch_player(player_id):
    player = next((x for x in machines if hasattr(x, 'session_id') and x.session_id == player_id), None)
    return player

def update_player(player_id, context='main'):
    player = fetch_player(player_id)
    player_json = copy.deepcopy(player).__dict__

    # this is disgusting. rasmus if you are reading this I'm sorry.
    if hasattr(player, 'outflow'):
        for i, outflow in enumerate(player.outflow):
            if outflow is not False:
                # outflow['material'].change_temp(0)
                player_json['outflow'][i] = {'amount': outflow['amount'], 'material': copy.deepcopy(outflow['material'].__dict__)}
                player_json['outflow'][i]['material']['name'] = outflow['material'].get_name()

    # again i am filled with remorse
    if hasattr(player, 'inputs'):
        for i, player_in in enumerate(player.inputs):
            if player_in is not False:
                # player_in['material'].change_temp(0)
                player_json['inputs'][i] = {'amount': player_in['amount'], 'material': copy.deepcopy(player_in['material'].__dict__)}
                player_json['inputs'][i]['material']['name'] = player_in['material'].get_name()


    if context=='main': emit('player_state', {'data': json.dumps(player_json)}, to=player_id)
    else: socketio.emit('player_state', {'data': json.dumps(player_json)}, to=player_id)

def update_world(context='main'):
    resolved_machines = network.resolve_network(machines)
    world_state = {'machines': [], 'connections': [], 'pool': [], 'win_state': win_state}

    for machine in resolved_machines:
        machine_json = copy.deepcopy(machine).__dict__

        # this is disgusting. rasmus if you are reading this I'm sorry.
        if hasattr(machine, 'outflow'):
            for i, outflow in enumerate(machine.outflow):
                if outflow is not False:
                    # outflow['material'].change_temp(0)
                    machine_json['outflow'][i] = {'amount': outflow['amount'], 'material': copy.deepcopy(outflow['material'].__dict__)}
                    machine_json['outflow'][i]['material']['name'] = outflow['material'].get_name()


        # again i am filled with remorse
        if hasattr(machine, 'inputs'):
            for i, machine_in in enumerate(machine.inputs):
                if machine_in is not False:
                    # machine_in['material'].change_temp(0)
                    machine_json['inputs'][i] = {'amount': machine_in['amount'], 'material': copy.deepcopy(machine_in['material'].__dict__)}
                    machine_json['inputs'][i]['material']['name'] = machine_in['material'].get_name()


        # screaming, crying, throwing up
        if hasattr(machine, 'recipes'): del machine_json['recipes']

        if hasattr(machine, 'pool'):
            # move the pool to its own thing
            del machine_json['pool']

            for i, material_type in enumerate(machine.pool):
                if material_type is not False:
                    world_state['pool'].append({'amount': material_type['amount'], 'material': copy.deepcopy(material_type['material'].__dict__)})
                    world_state['pool'][i]['material']['name'] = material_type['material'].get_name()

        world_state['machines'].append(machine_json)


    for connection in connections:
        world_state['connections'].append(connection.__dict__)

    check_win_state(world_state, context)

    # this is a hack to deal with the threading context.
    if context == 'main': emit('world_state', {'data': json.dumps(world_state)}, broadcast=True)
    else: socketio.emit('world_state', {'data': json.dumps(world_state)})

def initialise_grid():
    machines.append(inlet(str(network.machine_num()), 'inlet'))
    output = outlet(str(network.machine_num()), 'outlet')
    machines.append(output)

def tick():
    players = list(filter(lambda x: type(x).__name__ == 'core', machines))
    for player in players:
        player.update_energy(-1*energy_delta)
        update_player(player.session_id, context='thread')
        if not player.alive:
            game_over(player, context='thread')

def background_thread():
    count = 0
    with app.test_request_context():
        while True:
            socketio.sleep(5)
            count += 1
            tick()
            update_world( context='thread')

def remove_player(player_id):
    rm_player = fetch_player(player_id)
    if rm_player is not None: 
        machines.remove(rm_player)
        if rm_player.alive: log_event('core ' + rm_player.machine_id + ' has fled the box')

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
    update_world()
    update_player(request.sid)

@socketio.event
def request_status():
    player = update_player(request.sid)

@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

@socketio.event
def add_machine(data):
    global machines
    player = fetch_player(request.sid)
    machines, player = network.add_machine(data['machine_type'], machines, player)
    if not player.alive:
        game_over(player)
    update_world()

@socketio.event
def add_connection(conn_data):
    global machines, connections
    player = fetch_player(request.sid)
    print('adding connection, voting is', conn_data)
    machines, connections, player = network.add_connection(str(network.connection_num()), conn_data['source'], conn_data['dest'], conn_data['voting'], machines, connections, player)
    if not player.alive:
        game_over(player)
    update_world()

@socketio.event
def rm_connection(data):
    global machines, connections
    conn = next((x for x in connections if x.conn_id == data['conn_id']), None)
    if conn is not None:
        if not conn.voting:
            player = fetch_player(request.sid)
            machines, connections = network.remove_connection(conn, machines, connections, player)
            print('removing connection', data['conn_id'], request.sid)
            log_event('connection ' + data['conn_id'] + ' was removed by core ' + player.machine_id)
        else:
            feedback_message('you have to vote to remove this connection', request.sid)

    else: feedback_message('could not find connection with id', request.sid)

    update_world()

@socketio.event
def vote(data):
    conn_id = data['conn_id']
    print('voting', data['conn_id'], request.sid)
    conn = next((x for x in connections if x.conn_id == conn_id), None)
    conn.votes.append(request.sid)

    players = list(filter(lambda x: type(x).__name__ == 'core', machines))
    current_ids = list(map(lambda x:x.session_id, players))
    shared = list(set(current_ids).intersection(conn.votes))
    print(conn.votes, current_ids, shared)

    if(len(shared) >= len(current_ids)/2):
        network.remove_connection(conn, machines, connections, fetch_player(request.sid))
        log_event('connection ' + conn_id + ' was removed by popular vote')

    # check the votes against players still in game


@socketio.event
def chat(message):
    player = fetch_player(request.sid)
    emit('chat_msg', {'data': message['data'], 'sender': request.sid, 'machine_id': player.machine_id}, broadcast=True)

@socketio.on('disconnect')
def test_disconnect():
    remove_player(request.sid)

if __name__ == '__main__':
    initialise_grid()
    socketio.run(app)
