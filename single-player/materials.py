import copy

class Material:
	def __init__(self, base_temp):
		self.temp = base_temp
		self.temp_state = ''
		self.description = "You don't know much about this material"
		self.alive = False

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
			if hasattr(material, 'heat'):
				material.heat()
			else:
				material.temp_state = "hot"
		
		elif material.temp <= material.cold_temp:
			if hasattr(material, 'cool'):
				material.cool()
			else:
				material.temp_state = "cold"
		
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
		self.hot_temp = hot_temp
		self.cold_temp = cold_temp

class Colloid(Material):
	def __init__(self, base_temp, hot_temp=40, cold_temp=0):
		super().__init__(base_temp)
		self.can_freeze = False
		self.material_type = "colloid"
		self.hot_temp = hot_temp
		self.cold_temp = cold_temp

class Liquid(Material):
	def __init__(self, base_temp,  hot_temp=40, cold_temp=0, freeze_temp=-10, vapour_temp=200):
		super().__init__(base_temp)
		self.can_freeze = True
		self.material_type = "liquid"
		self.hot_temp = hot_temp
		self.cold_temp = cold_temp
		self.freeze_temp = freeze_temp
		self.vapour_temp = vapour_temp

class Gas(Material):
	def __init__(self, base_temp, freeze_temp=0):
		super().__init__(base_temp)
		self.can_freeze = True
		self.material_type = "gas"
		self.freeze_temp = freeze_temp

class Dirt(Solid):
	def __init__(self, base_temp=20, name='dirt'):
		super().__init__(base_temp, hot_temp=30)
		self.name = name
		self.description = "Grimy, stupid dirt. What are you going to do with this, idiot?"

	def dry(self):
		return Sand(base_temp = self.temp)

	def wet(self):
		return Leaf(base_temp = self.temp)

class Sand(Solid):
	def __init__(self, base_temp=20, name='sand'):
		super().__init__(base_temp, hot_temp=200)
		self.name = name
		self.description = "Fine, dry and gritty."

	def wet(self):
		return Dirt(base_temp = self.temp)

	def heat(self):
		return Glass(base_temp = self.temp)

class Glass(Solid):
	def __init__(self, base_temp=20, name='glass'):
		super().__init__(base_temp)
		self.name = name

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

	def compress(self):
		return BabyRat(base_temp = self.temp)


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

	def centrifuge(self):
		return Ammonia(), Salt(), SunsetYellow()

class Blood(Liquid):
	def __init__(self, base_temp=20, name='blood'):
		super().__init__(base_temp)
		self.name = name
		self.description = "Warm liquid gore. Is it yours? Is it theirs? At this point, who cares."

	def dry(self):
		return Scab(base_temp = self.temp)

class Teeth(Solid):
	def __init__(self, base_temp=20, name='teeth'):
		super().__init__(base_temp)
		self.name = name
		self.description = "Crunchier than you remember."

	def grind(self):
		return Sand(base_temp=self.temp)

class Pellet(Solid):
	def __init__(self, base_temp=20, name='pellet'):
		super().__init__(base_temp)
		self.name = name
		self.description = "God you love the pellets, don’t you? Crunch crunch crunch basic foodstuff, eh? Wouldn’t this be nice with a cold beer? Some piss? ha ha ha."

	def wet(self):
		return Slurry(base_temp=self.temp)
		

class Vomit(Liquid):
	def __init__(self, base_temp=20, name='vomit'):
		super().__init__(base_temp)
		self.name = name
		self.description = "What a waste. You could have made good use of those pellets"

	def dry(self):
		return Pellet(base_temp = self.temp)


class Concrete(Solid):
	def __init__(self, base_temp=20, name='concrete'):
		super().__init__(base_temp)
		self.name = name
		self.description = "Hard and unforgiving."

	def compress(self):
		return Rock(base_temp = self.temp)


class Leaf(Solid):
	def __init__(self, base_temp=20, name='leaf'):
		super().__init__(base_temp)
		self.name = name

	def compress(self):
		return Tobacco(base_temp=self.temp)

class Bug(Solid):
	def __init__(self, base_temp=20, name='bug'):
		super().__init__(base_temp)
		self.name = name
		self.alive = True

	def grind(self):
		return Starch(base_temp=self.temp)


class Starch(Solid):
	def __init__(self, base_temp=20, name='starch'):
		super().__init__(base_temp)
		self.name = name

	def wet(self):
		return Slurry(base_temp=self.temp)


class Rock(Solid):
	def __init__(self, base_temp=20, name='rock'):
		super().__init__(base_temp)
		self.name = name

	def compress(self):
		return Diamond(base_temp=self.temp+100)

class Asphalt(Solid):
	def __init__(self, base_temp=20, name='asphalt'):
		super().__init__(base_temp)
		self.name = name

class Computer(Solid):
	def __init__(self, base_temp=20, name='computer'):
		super().__init__(base_temp)
		self.name = name

	def grind(self):
		return Sand(base_temp=self.temp)

class Neuron(Solid):
	def __init__(self, base_temp=20, name='neuron'):
		super().__init__(base_temp)
		self.name = name

	def psychoactive_effect(player):
		feedback_message("ah fuck you've contracted Creuzfeld Jakob Disease")


class Prion(Solid):
	def __init__(self, base_temp=20, name='neuron'):
		super().__init__(base_temp)
		self.name = name

	def psychoactive_effect(player):
		feedback_message("ah fuck you've contracted Creuzfeld Jakob Disease")


class Oil(Liquid):
	def __init__(self, base_temp=20, name='oil'):
		super().__init__(base_temp)
		self.name = name

	def compress(self):
		return Fat(base_temp = self.temp)

	def distil(self):
		return Benzene(), Methane(), Alcohol()


class Ketamine(Solid):
	def __init__(self, base_temp=20, name='ketamine'):
		super().__init__(base_temp)
		self.name = name

class MCat(Solid):
	def __init__(self, base_temp=20, name='M-CAT'):
		super().__init__(base_temp)
		self.name = name

	def psychoactive_effect(player):
		player.dignity = player.dignity - 10

	def distil(self):
		return SyntheticCannabinoid(), Prozac(), GrowthHormone()

class Sweat(Liquid):
	def __init__(self, base_temp=20, name='sweat'):
		super().__init__(base_temp)
		self.name = name

	def centrifuge(self):
		print('centrifuging in material')
		return Ammonia(), Ketamine(), Salt()

class Ammonia(Liquid):
	def __init__(self, base_temp=20, name='ammonia'):
		super().__init__(base_temp)
		self.name = name

class Benzene(Liquid):
	def __init__(self, base_temp=20, name='benzene'):
		super().__init__(base_temp)
		self.name = name

class Tobacco(Solid):
	def __init__(self, base_temp=20, name='tobacco'):
		super().__init__(base_temp)
		self.name = name

	def compress(self):
		return Cigarette()

class Cigarette(Solid):
	def __init__(self, base_temp=20, name='cigarette'):
		super().__init__(base_temp)
		self.name = name

class Sweetener(Solid):
	def __init__(self, base_temp=20, name='M-CAT'):
		super().__init__(base_temp)
		self.name = name

class Flower(Solid):
	def __init__(self, base_temp=20, name='M-CAT'):
		super().__init__(base_temp)
		self.name = name
		self.alive = True

	def compress(self):
		return Oil(base_temp = self.temp)

class BabyRat(Solid):
	def __init__(self, base_temp=20, name='baby rat'):
		super().__init__(base_temp)
		self.name = name
		self.alive = True

	def grind(self):
		return Neuron(base_temp = self.temp)

class Corn(Solid):
	def __init__(self, base_temp=20, name='corn'):
		super().__init__(base_temp)
		self.name = name

	def grind(self):
		return Starch(base_temp = self.temp)

class Alcohol(Liquid):
	def __init__(self, base_temp=20, name='alcohol'):
		super().__init__(base_temp)
		self.name = name


class Slurry(Liquid):
	def __init__(self, base_temp=20, name='slurry'):
		super().__init__(base_temp)
		self.name = name

	def dry(self):
		return Pellet(base_temp = self.temp)

class SyntheticCannabinoid(Solid):
	def __init__(self, base_temp=20, name='synthetic cannabinoid'):
		super().__init__(base_temp)
		self.name = name


class Legs(Solid):
	def __init__(self, base_temp=20, name='legs'):
		super().__init__(base_temp)
		self.name = name

	def grind(self):
		return Flesh(base_temp = self.temp)


class Foam(Colloid):
	def __init__(self, base_temp=20, name='foam'):
		super().__init__(base_temp)
		self.name = name

	def compress(self):
		return Piss(base_temp=self.temp)


class Jelly(Colloid):
	def __init__(self, base_temp=20, name='jelly'):
		super().__init__(base_temp)
		self.name = name


class Salt(Solid):
	def __init__(self, base_temp=20, name='salt'):
		super().__init__(base_temp)
		self.name = name

	def wet(self):
		return Piss(base_temp=self.temp)


class Prozac(Solid):
	def __init__(self, base_temp=20, name='prozac'):
		super().__init__(base_temp)
		self.name = name

	def psychoactive_effect(player):
		player.morale = player.morale + 10


class Methane(Gas):
	def __init__(self, base_temp=20, name='methane'):
		super().__init__(base_temp)
		self.name = name

class Plastic(Solid):
	def __init__(self, base_temp=20, name='plastic'):
		super().__init__(base_temp)
		self.name = name

class Soap(Solid):
	def __init__(self, base_temp=20, name='soap'):
		super().__init__(base_temp)
		self.name = name

class Glue(Liquid):
	def __init__(self, base_temp=20, name='glue'):
		super().__init__(base_temp)
		self.name = name

	def dry(self):
		return Plastic(base_temp=self.temp)


class Centipede(Solid):
	def __init__(self, base_temp=20, name='centipede'):
		super().__init__(base_temp)
		self.name = name
		self.alive = True

	def grind(self):
		return Legs(base_temp=self.temp)

class SunsetYellow(Liquid):
	def __init__(self, base_temp=20, name='Sunset Yellow'):
		super().__init__(base_temp)
		self.name = name


class FastGreen(Liquid):
	def __init__(self, base_temp=20, name='Fast Green'):
		super().__init__(base_temp)
		self.name = name

class GrowthHormone(Liquid):
	def __init__(self, base_temp=20, name='growth hormone'):
		super().__init__(base_temp)
		self.name = name

	# should make player outputs and inputs double?

class ReconstitutedEgg(Solid):
	def __init__(self, base_temp=20, name='reconstituted egg'):
		super().__init__(base_temp)
		self.name = name

class Mayonnaise(Colloid):
	def __init__(self, base_temp=20, name='mayonnaise'):
		super().__init__(base_temp)
		self.name = name

	def centrifuge(self):
		return ReconstitutedEgg(), Oil(), Salt()

class Vape(Solid):
	def __init__(self, base_temp=20, name='growth hormone'):
		super().__init__(base_temp)
		self.name = name
		self.description="I strongly advise against giving any living creature, including rats, access to vaping devices or substances. Vaping involves inhaling aerosolized chemicals, which can be harmful to both humans and animals. \nRats have smaller respiratory systems and are more sensitive to airborne particles than humans, so exposing them to vaping aerosols could lead to serious health issues. There is a lack of research on the specific effects of vaping on rats, but it's reasonable to assume that it would be harmful to their health, just as it is for humans.\nIf you're concerned about the health and well-being of your rats or any animals, it's important to provide them with a safe and appropriate environment and avoid exposing them to potentially harmful substances. If you suspect that an animal has been exposed to something harmful, it's best to consult a veterinarian."

class FlaminHotCheeto(Solid):
	def __init__(self, base_temp=20, name='Flamin Hot Cheeto'):
		super().__init__(base_temp)
		self.name = name

	def grind(self):
		return Starch(base_temp = self.temp)

class DoritoCoolOriginal(Solid):
	def __init__(self, base_temp=20, name='Dorito Cool Original'):
		super().__init__(base_temp)
		self.name = name

	def grind(self):
		return Starch(base_temp = self.temp)

class MSG(Solid):
	def __init__(self, base_temp=20, name='MSG'):
		super().__init__(base_temp)
		self.name = name

	def psychoactive_effect(self, player):
		player.morale = player.morale + 1

class Nugget(Solid):
	def __init__(self, base_temp=20, name='nugget'):
		super().__init__(base_temp)
		self.name = name

	def grind(self):
		return Starch()

recipes = [
	Recipe({'piss', 'blood'}, Teeth()), 
	Recipe({'hot vomit', 'sand'}, Concrete()),
	Recipe({'bug', 'glue'}, Centipede()),
	Recipe({'ammonia', 'slurry'}, MCat()),
	Recipe({'ketamine', 'alcohol'}, Prozac()),
	Recipe({'benzene', 'tobacco'}, Vape()),
	Recipe({'alcohol', 'salt'}, Soap()),
	Recipe({'cigarette', 'computer'}, Vape()),
	Recipe({'soap', 'sweat'}, Foam()),
	Recipe({'sweetener', 'cigarette'}, Vape()),
	Recipe({'rock', 'oil'}, Asphalt()),
	Recipe({'rock', 'neuron'}, Computer()),
	Recipe({'Sunset Yellow', 'Fast Green'}, SyntheticCannabinoid()),
	Recipe({'mayonnaise', 'mayonnaise'}, ReconstitutedEgg()),
	Recipe({'legs', 'synthetic cannabinoid'}, Centipede()),
	Recipe({'piss', 'leaf'}, Alcohol()),
	Recipe({'dirt', 'leaf'}, Flower()),
	Recipe({'prozac', 'growth hormones'}, Mayonnaise()),
	Recipe({'oil', 'hot baby rat'}, Plastic()),
	Recipe({'ketamine', 'MSG'}, MCat()),
	Recipe({'foam', 'MSG'}, FlaminHotCheeto()),
	Recipe({'hot bugs', 'MSG'}, Nugget()),
]