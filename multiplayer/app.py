from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from components import *
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
    new_core = core(request.sid, 'you', initial_energy=300)
    machines.append(new_core)
    print('created core', new_core.machine_id)
    print('machines is now', machines)
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



@socketio.on('disconnect')
def test_disconnect():
    rem_core = next((x for x in machines if x.machine_id == request.sid), None)
    print('client disconnected; removing core', request.sid)
    machines.remove(rem_core)
    print('machines is now', machines)


if __name__ == '__main__':
    socketio.run(app)
