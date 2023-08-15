class Material:
	def __init__(self, base_temp):
		self.temp = base_temp

	def heat(self, amount):
		self.temp = self.temp + amount

class Recipe:
	def __init__(self, ingredients, result):
		self.ingredients = ingredients
		self.result = result

class Solid(Material):
	def __init__(self, base_temp):
		super().__init__(base_temp)
		self.can_freeze = False

class Liquid(Material):
	def __init__(self, base_temp):
		super().__init__(base_temp)
		self.can_freeze = True

class Dirt(Solid):
	def __init__(self, base_temp=20, name='dirt'):
		super().__init__(base_temp)
		self.name = name

	def dry(self):
		return Sand(base_temp = self.temp)

	def wet(self):
		return Muck(base_temp = self.temp)

class Sand(Solid):
	def __init__(self, base_temp=20, name='sand'):
		super().__init__(base_temp)
		self.name = name

	def wet(self):
		return Dirt(base_temp = self.temp)

class Muck(Liquid):
	def __init__(self, base_temp=20, name='muck'):
		super().__init__(base_temp)
		self.name = name

	def dry(self):
		return Dirt(base_temp = self.temp)

class Piss(Liquid):
	def __init__(self, base_temp=20, name='piss'):
		super().__init__(base_temp)
		self.name = name

class Blood(Liquid):
	def __init__(self, base_temp=20, name='blood'):
		super().__init__(base_temp)
		self.name = name

class Teeth(Solid):
	def __init__(self, base_temp=20, name='teeth'):
		super().__init__(base_temp)
		self.name = name

class Pellet(Solid):
	def __init__(self, base_temp=20, name='pellet'):
		super().__init__(base_temp)
		self.name = name

recipes = []
recipes.append(Recipe({'piss', 'blood'}, Teeth()))