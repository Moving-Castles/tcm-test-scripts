import copy

class Material(object):
	def __init__(self, base_temp):
		self.temp = base_temp
		self.temp_state = ''
		self.description = "You don't know much about this material"

	def change_temp(self, amount):
		material = copy.deepcopy(self)
		material.temp = material.temp + amount

		# deal with the extreme cases first
		if getattr(material, "freeze", None) is not None:
			if material.temp <= material.freeze_temp:
				frozen = material.freeze()
				return frozen

		if getattr(material, "vapourise", None) is not None:
			if material.temp >= material.vapour_temp:
				vapour = material.vapourise()
				return vapour

		if material.temp >= material.hot_temp:
			material.temp_state = "hot"
			self.temp_state = "hot"
		
		elif material.temp <= material.cold_temp:
			material.temp_state = "cold"
			self.temp_state = "cold"
		
		else:
			material.temp_state = ""
			self.temp_state = ''

		return material

	def get_name(self):
		material = self.change_temp(0)
		return (self.temp_state + " " + self.name).strip()


class Recipe(object):
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
		super().__init__(base_temp, hot_temp=30)
		self.name = name
		self.description = "Grimy, stupid dirt. What are you going to do with this, idiot?"

	def dry(self):
		return Sand(base_temp = self.temp)

	def wet(self):
		return Muck(base_temp = self.temp)

class Sand(Solid):
	def __init__(self, base_temp=20, name='sand'):
		super().__init__(base_temp)
		self.name = name
		self.description = "Fine, dry and gritty."

	def wet(self):
		return Dirt(base_temp = self.temp)


class Concrete(Solid):
	def __init__(self, base_temp=20, name='concrete'):
		super().__init__(base_temp)
		self.name = name
		self.description = "Hard and unforgiving."

class Scab(Solid):
	def __init__(self, base_temp=20, name='scab'):
		super().__init__(base_temp)
		self.name = name
		self.is_food = True
		self.description = "Coagulated lumpen cells. Delicious."

class Flesh(Solid):
	def __init__(self, base_temp=20, name='flesh'):
		super().__init__(base_temp)
		self.name = name
		self.description = "Wet, chewy, crunchy. A loose mass of fat and sinew. "

class Muck(Liquid):
	def __init__(self, base_temp=20, name='muck'):
		super().__init__(base_temp)
		self.name = name
		self.description = "Like dirt but even more useless. Jesus Fucking Christ."

	def dry(self):
		return Dirt(base_temp = self.temp)

class Piss(Liquid):
	def __init__(self, base_temp=20, name='piss', vapour_temp=90):
		super().__init__(base_temp, vapour_temp=90)
		self.name = name
		self.description = "Steaming, streaming, fresh excreta."

	def vapourise(self):
		print('turning to vapour')
		return Piss(base_temp = self.temp, name="noxious boiling piss vapour")

class Blood(Liquid):
	def __init__(self, base_temp=20, name='blood'):
		super().__init__(base_temp)
		self.name = name
		self.is_food = True
		self.description = "Warm liquid gore. Is it yours? Is it theirs? At this point, who cares."

	def dry(self):
		return Scab(base_temp = self.temp)


class Vomit(Liquid):
	def __init__(self, base_temp=20, name='vomit'):
		super().__init__(base_temp)
		self.name = name
		self.description = "What a waste. You could have made good use of those pellets"

	def dry(self):
		return Pellet(base_temp = self.temp)


class Gruel(Liquid):
	def __init__(self, base_temp=20, name='gruel'):
		super().__init__(base_temp)
		self.name = name
		self.description = "You don't like this as much as you like the pellets. But it's OK. Softer. Easier on your tired teeth."
		self.is_food = True

	def dry(self):
		return Pellet(base_temp = self.temp)

class Teeth(Solid):
	def __init__(self, base_temp=20, name='teeth'):
		super().__init__(base_temp)
		self.name = name
		self.description = "Crunchier than you remember."

class Pellet(Solid):
	def __init__(self, base_temp=20, name='pellet'):
		super().__init__(base_temp)
		self.name = name
		self.is_food = True
		self.description = "God you love the pellets, don’t you? Crunch crunch crunch basic foodstuff, eh? Wouldn’t this be nice with a cold beer? Some piss? ha ha ha."

	def wet(self):
		return Gruel(base_temp = self.temp)



recipes = [
	Recipe({'piss', 'blood'}, Teeth()), 
	Recipe({'hot vomit', 'sand'}, Concrete())
]