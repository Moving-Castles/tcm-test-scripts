import copy

class Player:
	def __init__(self, session_id, player_id):
		super().__init__()
		self.session_id = copy.deepcopy(session_id)
		self.id = player_id
		self.points = 1000
		self.materials = {
			'BUGS': 1000,
			'PISS': 100,
			'MDMA': 500
		}

	def getCurrentBids(self, listing):
		bids = {
			"sell_offers": [],
			"buy_offers": [],
			"buy_completed": [],
			"sell_completed": [],
		}

		for material in listing.sell_offers.keys():
			for offer in listing.sell_offers[material]:
				if offer.proposer.id == self.id:
					bids["sell_offers"].append(offer.asDict())

			for offer in listing.buy_offers[material]:
				if offer.proposer.id == self.id:
					bids["buy_offers"].append(offer.asDict())

		for tx in listing.completed_transactions:
			if tx.buyer.id == self.id:
				print('appending')
				bids["buy_completed"].append(tx.asDict())

			if tx.seller.id == self.id:
				bids["sell_completed"].append(tx.asDict())

		return bids

	def toJSON(self):
		return {
			'id': self.id,
			'points': self.points,
			'materials': self.materials
		}
