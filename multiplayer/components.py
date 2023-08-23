from materials import *
import copy
# from network import print_message, game_over


def print_message(message):
	print(message)

class Connection(object):
	def __init__(self, source, dest, conn_id):
		self.source = source
		self.dest = dest
		self.cost = 6
		self.vote_cost = 10
		self.votes = []
		self.conn_id = conn_id
		self.description = "Pumping your vile fluids from A to B."

	# if a player disconnects need to remove their vote from counting
	# or maybe there's just a live check on this?
	def vote(self, voter_id):
		self.votes.append(voter_id)

	def draw(self, machines):
		# check if there's space on the input of source
		# and on the output of dest. if not then
		for machine in machines:
			print(machine.machine_id, self.source, self.dest, type(machine.machine_id), type(self.source))

		machine = next((m for m in machines if m.machine_id == self.source), None)
		print('machine is', machine)
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


class Machine(object):
	def __init__(self):
		self.outflow = []
		self.can_remove = True
		self.description = "You don't know much about this machine"

class Organ(object):
	def __init__(self):
		self.outflow = []
		self.alive = True
		self.can_remove = False
		self.description = "You don't know much about this organ"

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

class parcher(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]
		self.cost = 20
		self.description = "Dessicates whatever enters its gaping maw."

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

class core(Organ):
	def __init__(self, machine_id, session_id, name, initial_energy=100):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.session_id = copy.deepcopy(session_id)
		self.outputs = [False, False]
		self.energy = initial_energy
		self.description = "That’s you, how about you hook some pipes up to those nice stumps of yours and get to work?"

	def process(self):
		if self.inputs[0]['material'].is_food:
			self.update_energy(self.inputs[0]['amount']*0.2)
			self.outflow = [{ 'material': Piss(), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Blood(), 'amount': self.inputs[0]['amount']*0.4}]
			return [{ 'material': Piss(), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Blood(), 'amount': self.inputs[0]['amount']*0.4}]
		else:
			print('ugh! not food!')
			self.outflow = copy.deepcopy(self.inputs)
			return self.inputs

	def update_energy(self, amount):
		self.energy = round(self.energy + amount, 1)
		if(self.energy <= 0):
			self.die()

	def remove_machine(self):
		print_message("nice try, asshole")
		# self.die()

	def die(self):
		self.alive = False

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
		self.inputs = [{'amount': 1.0, 'material': Pellet()}]
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