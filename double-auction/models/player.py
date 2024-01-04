import copy

class Player:
	def __init__(self, session_id):
		super().__init__()
		self.session_id = copy.deepcopy(session_id)
		self.points = 1000