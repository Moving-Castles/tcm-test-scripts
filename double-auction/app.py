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

# need to explicitly invoke socketio here as it's a separate thread
def background_thread():
	count = 0
	with app.test_request_context():
		while True:
			print('tick')
			socketio.sleep(5)
			# get prices and send
			listing.trackMarketPrices()
			socketio.emit('price_info', {"data": json.dumps(listing.price_history, sort_keys=True, default=str)})

			for player in players:
				player.materials['BUGS'] -= 5
				socketio.emit('player_info', {'data': json.dumps(player.toJSON(), sort_keys=True, default=str), 'bids': json.dumps(player.getCurrentBids(listing), sort_keys=True, default=str)}, to=player.session_id)
				# socketio.emit('log_event', {'data': 'bug rental collected'}, to=player.session_id)


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
	emit('player_info', {'data': json.dumps(new_player.toJSON(), sort_keys=True, default=str), 'bids': json.dumps(new_player.getCurrentBids(listing), sort_keys=True, default=str)})
	print('created new player, players are', players)

@socketio.event
def convert(msg):
	player = fetch_player(request.sid)
	# feedback_msg = player.convert(msg["from"], msg["to"])
	bids = player.getCurrentBids(listing)

	if msg["from"] == 'BUGS' and msg["to"] == 'PISS':
		if player.materials['BUGS'] >= 10:
			player.materials['BUGS'] -= 10
			player.materials['PISS'] += player.level*0.1*10
			emit('player_info', {'data': json.dumps(player.toJSON(), sort_keys=True, default=str), 'bids': json.dumps(bids, sort_keys=True, default=str)}, to=player.session_id)
		else:
			emit('log_event', {'data': "insufficient BUGS to connvert"})

	if msg["from"] == 'PISS' and msg["to"] == 'MDMA':
		if player.materials['PISS'] >= 10:
			player.materials['PISS'] -= 10
			player.materials['MDMA'] += player.level*0.1*10
			emit('player_info', {'data': json.dumps(player.toJSON(), sort_keys=True, default=str), 'bids': json.dumps(bids, sort_keys=True, default=str)}, to=player.session_id)
		else:
			emit('log_event', {'data': "insufficient PISS to connvert"})

@socketio.event
def buy_bugs(msg):
	player = fetch_player(request.sid)
	# feedback_msg = player.convert(msg["from"], msg["to"])
	bids = player.getCurrentBids(listing)
	amount = msg["volume"]

	if player.points >= amount:
		player.points -= amount
		player.materials['BUGS'] += amount
		emit('player_info', {'data': json.dumps(player.toJSON(), sort_keys=True, default=str), 'bids': json.dumps(bids, sort_keys=True, default=str)}, to=player.session_id)

	else:
		emit('log_event', {'data': "insufficient points"})


@socketio.event
def sell_piss(msg):
	player = fetch_player(request.sid)
	# feedback_msg = player.convert(msg["from"], msg["to"])
	bids = player.getCurrentBids(listing)
	amount = msg["volume"]

	if player.materials['PISS'] >= amount:
		player.points += 12
		player.materials['PISS'] -= amount
		emit('player_info', {'data': json.dumps(player.toJSON(), sort_keys=True, default=str), 'bids': json.dumps(bids, sort_keys=True, default=str)}, to=player.session_id)

	else:
		emit('log_event', {'data': "insufficient PISS"})


@socketio.event
def sell_mdma(msg):
	player = fetch_player(request.sid)
	# feedback_msg = player.convert(msg["from"], msg["to"])
	bids = player.getCurrentBids(listing)
	amount = msg["volume"]

	if player.materials['MDMA'] >= amount:
		player.points += 130
		player.materials['MDMA'] -= amount
		emit('player_info', {'data': json.dumps(player.toJSON(), sort_keys=True, default=str), 'bids': json.dumps(bids, sort_keys=True, default=str)}, to=player.session_id)

	else:
		emit('log_event', {'data': "insufficient MDMA"})


@socketio.event
def offer(offer):
	print('offer is', json.dumps(offer, sort_keys=True, default=str))
	# check player can complete bid and put in escrow
	bidder = fetch_player(request.sid)

	# check valid offer
	# has funds / materials
	# player is not maxed out of active bids
	current_bids = bidder.getCurrentBids(listing)

	try:
		int(offer['volume'])
	except:
		emit('log_event', {'data': 'can only trade materials in whole units'})
		return	

	try:
		if (len(current_bids["buy_offers"]) + len(current_bids["sell_offers"]) > 5):
			emit('log_event', {'data': 'max active bids reached'})
			return

		if offer['type'] == 'BUY':
			offer_cost = int(offer['volume'])*float(offer['unit_price'])
			if bidder.points >= offer_cost:
				bidder.points -= offer_cost

			else:
				emit('log_event', {'data': 'insufficient funds'})
				return

		if offer['type'] == 'SELL':
			if bidder.materials[offer['material']] >= int(offer['volume']):
				bidder.materials[offer['material']] -= int(offer['volume'])

			else:
				emit('log_event', {'data': 'insufficient ' + offer['material'] + ' to complete transaction'})
				return

		# try:

		new_offer = Offer()
		new_offer.setOfferDetails(OfferType[offer['type']], Materials[offer['material']], float(offer['unit_price']), int(offer['volume']), bidder)
		listing.addOffer(new_offer)

		emit('log_event', {'data': 'successfully placed ' + offer['type'] + ' offer for ' + str(offer['volume']) + ' ' + offer['material'] + ' at a unit price of ' + str(offer['unit_price'])})
		emit('tx_state', {'data': json.dumps(listing.txToJSON(), sort_keys=True, default=str)}, broadcast=True)

		print('price tracker')

		for player in players:
			print('emitting to', player.id, player.session_id)
			bids = player.getCurrentBids(listing)
			emit('player_info', {'data': json.dumps(player.toJSON(), sort_keys=True, default=str), 'bids': json.dumps(bids, sort_keys=True, default=str)}, to=player.session_id)

	except Exception as e: 
		print(e)
		emit('log_event', {'data': 'invalid bid format'})

@socketio.event
def connect():
	global thread
	with thread_lock:
		print('connected')
		if thread is None:
			print('startin thread')
			thread = socketio.start_background_task(background_thread)

@socketio.event
def disconnect():
	print('removing player', request.sid)
	remove_player(request.sid)

if __name__ == '__main__':
	socketio.run(app)