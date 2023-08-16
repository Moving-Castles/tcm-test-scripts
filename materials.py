import copy

class Material:
	def __init__(self, base_temp):
		self.temp = base_temp
		self.temp_state = ''

	def change_temp(self, amount):
		material = copy.deepcopy(self)
		print('changing temp', material.temp, amount)
		material.temp = material.temp + amount
		print('temp is now', material.temp, 'hot temp is', material.hot_temp)

		# deal with the extreme cases first
		if getattr(material, "freeze", None) is not None:
			if material.temp <= material.freeze_temp:
				frozen = material.freeze()
				print('returning')
				return frozen

		print('gets here')
		if getattr(material, "vapourise", None) is not None:
			if material.temp >= material.vapour_temp:
				vapour = material.vapourise()
				print('returning vaput')
				return vapour

		print('gets here')
		if material.temp >= material.hot_temp:
			material.temp_state = "hot"
			print('changed name')
		elif material.temp <= material.cold_temp:
			material.temp_state = "cold"
			print('changed name')
		else:
			material.temp_state = ""

		return material

	def get_name(self):
		return (self.temp_state + " " + self.name).strip()


class Recipe:
	def __init__(self, ingredients, result):
		self.ingredients = ingredients
		self.result = result

class Solid(Material):
	def __init__(self, base_temp, hot_temp=40, cold_temp=0):
		super().__init__(base_temp)
		self.can_freeze = False
		self.material_type = "solid"
		self.is_food = False # by default
		self.hot_temp = hot_temp
		self.cold_temp = cold_temp

class Liquid(Material):
	def __init__(self, base_temp,  hot_temp=40, cold_temp=0, freeze_temp=-10, vapour_temp=200):
		super().__init__(base_temp)
		self.can_freeze = True
		self.material_type = "liquid"
		self.is_food = False
		self.hot_temp = hot_temp
		self.cold_temp = cold_temp
		self.freeze_temp = freeze_temp
		self.vapour_temp = vapour_temp

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
	def __init__(self, base_temp=20, name='piss', vapour_temp=90):
		super().__init__(base_temp, vapour_temp=90)
		self.name = name

	def vapourise(self):
		print('turning to vapour')
		return Piss(base_temp = self.temp, name="noxious boiling piss vapour")

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
		self.is_food = True

recipes = []
recipes.append(Recipe({'piss', 'blood'}, Teeth()))