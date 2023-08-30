from materials import *
import copy
from network import print_message, game_over

class Connection():
	def __init__(self, source, dest, conn_id):
		self.source = source
		self.dest = dest
		self.cost = 6
		self.conn_id = conn_id
		self.description = "Pumping your vile fluids from A to B."

	def draw(self, machines):
		# check if there's space on the input of source
		# and on the output of dest. if not then

		machine = next((m for m in machines if m.machine_id == self.source), None)
		if machine is not None:
			# check if you can actually put it on the output
			try:
				in_idx = machine.outputs.index(False)
				machine.outputs[in_idx] = self.dest
			except:
				print_message("pipe was not added -- no available outputs on source machine")
				return False

			# now check if you can find the target
			rx_node = next((x for x in machines if x.machine_id == self.dest), None)
			if rx_node is not None:
				try:
					in_idx = rx_node.inputs.index(False)
				except:
					print_message("pipe was not added -- no available inputs on target machine")
					return False
			else:
				print_message("pipe was not added -- couldn't find target machine")
				return False

		else:
			print_message("pipe was not added -- couldn't find source machine")
			return False

		return True

	def remove_conn(self, machines):
		source_machine = next((m for m in machines if m.machine_id == self.source), None)
		if source_machine is not None:
			try:
				in_idx = source_machine.outputs.index(self.dest)
				source_machine.outputs[in_idx] = False
			except:
				print_message("pipe was not removed -- couldn't find target machine")
				return
		else:
			print_message("pipe was not removed -- couldn't find source machine")


class Machine:
	def __init__(self):
		self.outflow = []
		self.cost = 50
		self.can_remove = True
		self.description = "You don't know much about this machine"


class scorcher(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]
		self.heating_power = 30
		self.cost = 30
		self.description = "A sweltering, hellish box."

	def process(self):
		material = self.inputs[0]['material'].change_temp(self.heating_power)
		self.outflow =  [{'material': material, 'amount': self.inputs[0]['amount']}]
		return [{'material': material, 'amount': self.inputs[0]['amount']}]


class refrigerator(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]
		self.heating_power = -30
		self.cost = 30
		self.description = "Drains the heat from materials."

	def process(self):
		material = self.inputs[0]['material'].change_temp(self.heating_power)
		self.outflow =  [{'material': material, 'amount': self.inputs[0]['amount']}]
		return [{'material': material, 'amount': self.inputs[0]['amount']}]

class parcher(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]
		self.cost = 20
		self.description = "Dessicates whatever enters its gaping maw."


	# rework this
	def process(self):
		material = self.inputs[0]['material']
		if getattr(material, "dry", None) is not None:
			material = material.dry()
		else: print('cannot dry')
		self.outflow = [{'material': material, 'amount': self.inputs[0]['amount']}]
		return [{'material': material, 'amount': self.inputs[0]['amount']}]

class splitter(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False, False]
		self.cost = 15
		self.description = "Split up the juices."

	def process(self):
		self.outflow = [{ 'amount': self.inputs[0]['amount']/2, 'material': self.inputs[0]['material']}, 
		{ 'amount': self.inputs[0]['amount']/2, 'material': self.inputs[0]['material']}]
		return [{ 'amount': self.inputs[0]['amount']/2, 'material': self.inputs[0]['material']}, 
		{ 'amount': self.inputs[0]['amount']/2, 'material': self.inputs[0]['material']}]


class blender(Machine):
	def __init__(self, machine_id, name, recipes=recipes):
		super().__init__()
		self.inputs = [False, False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]
		self.recipes = recipes
		self.cost = 40
		self.description = "Crunching and mashing into a uniform pulp. Results may vary."

	def process(self):
		ingredients = {self.inputs[1]['material'].name, self.inputs[0]['material'].name}
		result = Dirt()
		for recipe in self.recipes:
			if recipe.ingredients == ingredients:
				result = recipe.result

		if self.inputs[0]['amount'] > self.inputs[1]['amount']:
			self.outflow = [{'material': result, 'amount': self.inputs[1]['amount']*2}]
			return [{'material': result, 'amount': self.inputs[1]['amount']*2}]

		else:
			self.outflow = [{'material': result, 'amount': self.inputs[0]['amount']*2}]
			return [{'material': result, 'amount': self.inputs[0]['amount']*2}]


class combi_gate(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False, False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]
		self.cost = 15

	def process(self):
		print('sent:')
		for out in self.inputs:
			print('  -  ', out['amount'], out['material'].name)

		print('to outlet')
		self.outflow = copy.deepcopy(self.inputs)
		return self.inputs


class inlet(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [{'amount': 10.0, 'material': Bug()}]
		self.name = 'inlet'
		self.machine_id = machine_id
		self.outputs = [False]
		self.description = "Special resource inlet."

	def remove_machine():
		print_message('you jam your stump into the pipe and the inflow slurps to a stop')

	def process(self):
		self.outflow = copy.deepcopy(self.inputs)
		return self.inputs


class outlet(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.pool = []
		self.name = name
		self.machine_id = machine_id
		self.outputs = []
		self.can_remove = False
		self.description = "Streaming bile duct, pipe in the fruits of your labour here."

	def remove_machine():
		print_message('your stumps scrape uselessly at the pipe, you cannot remove it')

	def process(self):
		if self.inputs[0] != False:
			pool_material = next((o for o in self.pool if o['material'].get_name() == self.inputs[0]['material'].get_name()), None)
			if pool_material is not None:
				pool_material['amount'] = round(pool_material['amount'] + self.inputs[0]['amount'], 1)
			else:
				self.pool.append(self.inputs[0])


class grinder(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]
		self.cost = 50

	def process(self):
		material = copy.deepcopy(self.inputs[0]['material'])
		if hasattr(self.inputs[0]['material'], "grind"):
			self.outflow = [{'material': material.grind(), 'amount': self.inputs[0]['amount']}] 
			return [{'material': material.grind(), 'amount': self.inputs[0]['amount']}] 

		else:
			self.outflow = [{'material': Slurry(), 'amount': self.inputs[0]['amount']}]
			return [{'material': Slurry(), 'amount': self.inputs[0]['amount']}]


class compressor(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]
		self.cost = 40

	def process(self):
		material = copy.deepcopy(self.inputs[0]['material'])
		if hasattr(material, "compress"):
			self.outflow = [{'material': material.grind(), 'amount': self.inputs[0]['amount']}]
			return [{'material': material.grind(), 'amount': self.inputs[0]['amount']}] 

		else:
			self.outflow = [{'material': material.grind(), 'amount': self.inputs[0]['amount']}]			
			return [{'material': Slurry(), 'amount': self.inputs[0]['amount']}]


class centrifuge(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False, False, False]
		self.cost = 150

	def process(self):
		material = copy.deepcopy(self.inputs[0]['material'])
		if material.name == 'uranium': self.stuxnet() # shouldn't just be a property on uranium as need to propagate

		if hasattr(material, "centrifuge"):
			out1, out2, out3 = material.centrifuge()
			print('centrifuging', out1, out2, out3)
			# one primary and 2 secondary materials
			self.outflow = [{'material': out1, 'amount': round(self.inputs[0]['amount']/2, 2)},
				{'material': out2, 'amount': round(self.inputs[0]['amount']/4, 2)},
				{'material': out3, 'amount': round(self.inputs[0]['amount']/4, 2)}]
			return [{'material': out1, 'amount': round(self.inputs[0]['amount']/2, 2)},
				{'material': out2, 'amount': round(self.inputs[0]['amount']/4, 2)},
				{'material': out3, 'amount': round(self.inputs[0]['amount']/4, 2)}]


	def stuxnet(self):
		feedback_message('o shit')


class distillation_column(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False, False, False]
		self.cost = 200

	def process(self):
		material = copy.deepcopy(self.inputs[0]['material'])
		if hasattr(material, "distil"):
			out1, out2, out3 = material.distil()
			self.outflow = [{'material': out1, 'amount': round(self.inputs[0]['amount']*0.1, 2)},
				{'material': out2, 'amount': round(self.inputs[0]['amount']*0.4, 2)},
				{'material': out3, 'amount': round(self.inputs[0]['amount']*0.5, 2)}]
			return [{'material': out1, 'amount': round(self.inputs[0]['amount']*0.1, 2)},
				{'material': out2, 'amount': round(self.inputs[0]['amount']*0.4, 2)},
				{'material': out3, 'amount': round(self.inputs[0]['amount']*0.5, 2)}]


##### ORGANS
class Organ:
	def __init__(self):
		self.outflow = []
		self.can_eat = ['pellet']
		self.alive = True
		self.can_remove = False
		self.description = "You don't know much about this organ"
		self.dignity = 0
		self.morale = 0
		self.neurotoxins = ['prion', 'neuron']

	def update_energy(self, amount):
		self.energy = round(self.energy + amount, 1)

		if(self.energy <= 0):
			self.die()

	def die(self):
		self.alive = False


class core(Organ):
	def __init__(self, machine_id, name, initial_energy=100):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False, False]
		self.energy = initial_energy
		self.can_eat = ['bug', 'pellet', 'nuggets', 'Doritos Cool Original', 'jelly', 'Flamin Hot Cheetos']
		self.description = "That’s you, how about you hook some pipes up to those nice stumps of yours and get to work?"

	def process(self):
		material = copy.deepcopy(self.inputs[0]['material'])

		if hasattr(material, 'psychoactive_effect'):
			material.psychoactive_effect(self)

		## need to add special functions for vape, cigarette, growth hormone, neuron, prion
		if material.name in self.can_eat and material.temp_state == 'hot':
			self.update_energy(self.inputs[0]['amount']*0.2)
			self.outflow = [{ 'material': Sweat(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Blood(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}]
			return [{ 'material': Sweat(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Blood(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}]

		if material.name in self.can_eat:
			self.update_energy(self.inputs[0]['amount']*0.2)
			self.outflow = [{ 'material': Piss(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Blood(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}]
			return [{ 'material': Piss(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Blood(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}]

		elif material.name in self.neurotoxins:
			feedback_message("Oops, that's a neurotoxin. Your brains start bubbling out of your ears")
			self.update_energy(-50)
			self.outflow = [{ 'material': Prion(base_temp=35), 'amount': round(self.inputs[0]['amount']*0.7, 2)},
				{'material': Jelly(base_temp=35), 'amount': self.inputs[0]['amount']*0.1}]
			return  [{ 'material': Prion(base_temp=35), 'amount': round(self.inputs[0]['amount']*0.7, 2)},
				{'material': Jelly(base_temp=35), 'amount': self.inputs[0]['amount']*0.1}]

		else:
			self.update_energy(-5)
			self.outflow = [{ 'material': Vomit(base_temp=35), 'amount': round(self.inputs[0]['amount']*0.7, 2)},
				{'material': Blood(base_temp=35), 'amount': self.inputs[0]['amount']*0.1}]
			return  [{ 'material': Vomit(base_temp=35), 'amount': round(self.inputs[0]['amount']*0.7, 2)},
				{'material': Blood(base_temp=35), 'amount': self.inputs[0]['amount']*0.1}]

	def remove_machine(self):
		print_message("you idiot!!!!!")
		self.die()

	def die(self):
		self.alive = False
		game_over()


class rat(Organ):
	def __init__(self, machine_id, name, initial_energy=100):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.cost = 50
		self.machine_id = machine_id
		self.outputs = [False, False]
		self.energy = initial_energy
		self.can_eat = ['glue', 'M-CAT', 'ketamine', 'synthetic cannabinoid', 'scab']
		self.description = "I think he's getting paid more than you..."

	def process(self):
		# special materials first
		if self.inputs[0]['material'].name == 'vape':
			self.outflow = [{ 'material': GrowthHormone(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Ammonia(), 'amount': self.inputs[0]['amount']*0.4}]
			return [{ 'material': GrowthHormone(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Ammonia(), 'amount': self.inputs[0]['amount']*0.4}]

		elif self.inputs[0]['material'].name in self.can_eat:
			self.update_energy(self.inputs[0]['amount']*0.2)
			self.outflow = [{ 'material': BabyRat(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Ammonia(), 'amount': self.inputs[0]['amount']*0.4}]
			return [{ 'material': BabyRat(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Ammonia(), 'amount': self.inputs[0]['amount']*0.4}]

		elif material.name in self.neurotoxins:
			self.update_energy(-10)
			self.outflow = [{ 'material': Prion(base_temp=35), 'amount': round(self.inputs[0]['amount']*0.7, 2)},
				{'material': Jelly(base_temp=35), 'amount': self.inputs[0]['amount']*0.1}]
			return  [{ 'material': Prion(base_temp=35), 'amount': round(self.inputs[0]['amount']*0.7, 2)},
				{'material': Jelly(base_temp=35), 'amount': self.inputs[0]['amount']*0.1}]

		else:
			print("can't eat that")
			self.update_energy(-5)
			self.outflow = [{ 'material': Foam(), 'amount': self.inputs[0]['amount']*0.5}, 
				{ 'material': Scab(), 'amount': self.inputs[0]['amount']*0.3}]
			return [{ 'material': Foam(), 'amount': self.inputs[0]['amount']*0.5}, 
				{ 'material': Scab(), 'amount': self.inputs[0]['amount']*0.3}]
			return self.inputs


class cow(Organ):
	def __init__(self, machine_id, name, initial_energy=100):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.cost = 100
		self.can_eat = ["slurry", "foam"]
		self.machine_id = machine_id
		self.outputs = [False, False]
		self.energy = initial_energy
		self.description = "ah, this must be who left the cowpat in the employee break room"

	def process(self):
		if self.inputs[0]['material'].name in self.can_eat:
			self.update_energy(self.inputs[0]['amount']*0.2)
			self.outflow = [{ 'material': Milk(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Methane(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}]
			return [{ 'material': Milk(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Methane(base_temp=35), 'amount': self.inputs[0]['amount']*0.4}]

		elif material.name in self.neurotoxins:
			self.update_energy(-10)
			self.outflow = [{ 'material': Prion(base_temp=35), 'amount': round(self.inputs[0]['amount']*0.7, 2)},
				{'material': Jelly(base_temp=35), 'amount': self.inputs[0]['amount']*0.1}]
			return  [{ 'material': Prion(base_temp=35), 'amount': round(self.inputs[0]['amount']*0.7, 2)},
				{'material': Jelly(base_temp=35), 'amount': self.inputs[0]['amount']*0.1}]

		else:
			self.update_energy(-5)
			self.outflow = [{ 'material': Slurry(base_temp=35), 'amount': round(self.inputs[0]['amount']*0.7, 2)},
				{'material': Methane(base_temp=35), 'amount': self.inputs[0]['amount']*0.1}]
			return  [{ 'material': Slurry(base_temp=35), 'amount': round(self.inputs[0]['amount']*0.7, 2)},
				{'material': Methane(base_temp=35), 'amount': self.inputs[0]['amount']*0.1}]