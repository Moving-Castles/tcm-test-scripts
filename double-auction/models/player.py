import copy

class Player:
	def __init__(self, session_id):
		super().__init__()
		self.session_id = copy.deepcopy(session_id)
		self.points = 1000
		self.materials = {
			'BUGS': 100,
			'PISS': 0,
			'MDMA': 0
		}
