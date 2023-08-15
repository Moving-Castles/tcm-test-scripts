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
		self.material_type = "solid"
		self.isFood = False # by default

class Liquid(Material):
	def __init__(self, base_temp):
		super().__init__(base_temp)
		self.can_freeze = True
		self.material_type = "liquid"

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

class Scab(Solid):
	def __init__(self, base_temp=20, name='scab'):
		super().__init__(base_temp)
		self.name = name

class Flesh(Solid):
	def __init__(self, base_temp=20, name='flesh'):
		super().__init__(base_temp)
		self.name = name

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

	def dry(self):
		return Scab(base_temp = self.temp)

class Teeth(Solid):
	def __init__(self, base_temp=20, name='teeth'):
		super().__init__(base_temp)
		self.name = name

class Pellet(Solid):
	def __init__(self, base_temp=20, name='pellet'):
		super().__init__(base_temp)
		self.name = name
		self.isFood = True

recipes = []
recipes.append(Recipe({'piss', 'blood'}, Teeth()))