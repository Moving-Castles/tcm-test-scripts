from threading import Lock
from flask import Flask, render_template, session, request, \
	copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
	close_room, rooms, disconnect
from models.player import *
from constants.offer_type import * 
from constants.materials import *
from models.offer import * 
from models.listing import * 
import json

async_mode = "gevent"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)#, async_mode=async_mode)
thread = None
thread_lock = Lock()
players = []
listing = Listing()
player_id = 0

def fetch_player(player_id):
	for player in players:
		print('sess', player.session_id)
	player = next((x for x in players if hasattr(x, 'session_id') and x.session_id == player_id), None)
	return player

def log_event(event):
	print('logging', event)
	socketio.emit('log_event', {'data': event})

def background_thread():
	count = 0
	with app.test_request_context():
		while True:
			socketio.sleep(5)
			# print('tick')

def remove_player(player_id):
	rm_player = fetch_player(player_id)
	if rm_player is not None: 
		players.remove(rm_player)
		# if rm_player.alive: log_event('core ' + player_id + ' has fled the box')

@app.route('/')
def index():
	return render_template('index.html', async_mode=socketio.async_mode)

@socketio.event
def chat(message):
	player = fetch_player(request.sid)
	emit('chat_msg', {'data': message['data'], 'sender': request.sid, 'machine_id': player_id}, broadcast=True)

@socketio.event
def create_player():
	global player_id
	print('makin player')
	player_id += 1
	new_player = Player(request.sid, player_id)
	players.append(new_player)
	emit('player_info', {'data': json.dumps(new_player.toJSON())})
	print('created new player, players are', players)

@socketio.event
def offer(offer):
	print('offer is', json.dumps(offer))
	# check player can complete bid and put in escrow

	# try:
	new_offer = Offer()
	new_offer.setOfferDetails(OfferType[offer['type']], Materials[offer['material']], int(offer['unit_price']), int(offer['num_units']), fetch_player(request.sid))
	listing.addOffer(new_offer)

	emit('log_event', {'data': 'successfully placed ' + offer['type'] + ' offer for ' + str(offer['num_units']) + ' ' + offer['material'] + ' at a unit price of ' + str(offer['unit_price'])})
	emit('tx_state', {'data': json.dumps(listing.txToJSON())})

	for player in players:
		print('emitting to', player.id, player.session_id)
		bids = player.getCurrentBids(listing)
		emit('bid_info', {'data':  json.dumps(bids)}, to=player.session_id)
	# except:
	# 	emit('log_event', {'data': 'invalid offer type'})

@socketio.event
def connect():
	global thread
	with thread_lock:
		print('connected')
		if thread is None:
			thread = socketio.start_background_task(background_thread)

@socketio.event
def disconnect():
	print('removing player', request.sid)
	remove_player(request.sid)

if __name__ == '__main__':
	socketio.run(app)