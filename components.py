from materials import *
import copy

class Connection():
	def __init__(self, source, dest):
		self.source = source
		self.dest = dest
		self.cost = 3

	def draw(self, machines):
		# check if there's space on the input of source
		# and on the output of dest. if not then

		machine = next((m for m in machines if m.machine_id == self.source), None)
		if machine is not None:
			print('machine outputs', machine.outputs)
			in_idx = machine.outputs.index(False)
			machine.outputs[in_idx] = self.dest
			print('machine outputs after connection', machine.outputs)
			print('connected', machine.name, (machine.machine_id), 'to', self.dest)
		else:
			print("couldn't find source machine")


	def delete(self, machines):
		# remove
		print('deleting', self.source, self.dest)

class Machine:
	def __init__(self):
		self.outflow = []


class Organ:
	def __init__(self):
		self.outflow = []
		self.alive = True


class scorcher(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]
		self.heating_power = 30
		self.cost = 30

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
	def __init__(self, machine_id, name, initial_energy):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False, False]
		self.energy = initial_energy

	def process(self):
		if self.inputs[0]['material'].is_food:
			self.update_energy(self.inputs[0]['amount']*0.2)
			self.outflow = [{ 'material': Piss(), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Blood(), 'amount': self.inputs[0]['amount']*0.4}]
			return [{ 'material': Piss(), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Blood(), 'amount': self.inputs[0]['amount']*0.4}]
		else:
			print('ugh! not food!')
			self.outflow = self.inputs
			return self.inputs

	def update_energy(self, amount):
		self.energy = round(self.energy + amount, 1)

		if(self.energy <= 0):
			self.die()

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
		self.outflow = self.inputs
		return self.inputs


class inlet(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [{'amount': 1.0, 'material': Pellet()}]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]

	def process(self):
		self.outflow = self.inputs
		return self.inputs

class outlet(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.pool = []
		self.name = name
		self.machine_id = machine_id
		self.outputs = []

	def process(self):
		if self.inputs[0] != False:
			pool_material = next((o for o in self.pool if o['material'].get_name() == self.inputs[0]['material'].get_name()), None)
			if pool_material is not None:
				pool_material['amount'] = round(pool_material['amount'] + self.inputs[0]['amount'], 1)
			else:
				self.pool.append(self.inputs[0])