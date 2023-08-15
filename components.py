from materials import *
import copy

class Connection():
	def __init__(self, source, dest):
		self.source = source
		self.dest = dest

	def draw(self, machines):
		# check if there's space on the input of source
		# and on the output of dest. if not then

		machine = next((m for m in machines if m.machine_id == self.source), None)
		if machine is not None:
			in_idx = machine.outputs.index(False)
			machine.outputs[in_idx] = self.dest
			print('connected', machine.name, (machine.machine_id), 'to', self.dest)
		else:
			print("couldn't find source machine")


	def delete(self, machines):
		# remove
		print('deleting', self.source, self.dest)

class Machine:
	def __init__(self):

		self.outflow = []

class heater(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]

	def process(self):
		material = copy.deepcopy(self.inputs[0]['material'])
		material.name = "hot " + material.name
		self.outflow =  [{'material': material, 'amount': self.inputs[0]['amount']}]
		return [{'material': material, 'amount': self.inputs[0]['amount']}]

class dryer(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]

	def process(self):
		material = self.inputs[0]['material']
		if getattr(material, "dry", None) is not None:
			material = material.dry()
		else: print('cannot dry')
		self.outflow = [{'material': material, 'amount': self.inputs[0]['amount']}]
		return [{'material': material, 'amount': self.inputs[0]['amount']}]

class split_gate(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False, False]

	def process(self):
		self.outflow = [{ 'amount': self.inputs[0]['amount']/2, 'material': self.inputs[0]['material']}, 
		{ 'amount': self.inputs[0]['amount']/2, 'material': self.inputs[0]['material']}]
		return [{ 'amount': self.inputs[0]['amount']/2, 'material': self.inputs[0]['material']}, 
		{ 'amount': self.inputs[0]['amount']/2, 'material': self.inputs[0]['material']}]


class mixer(Machine):
	def __init__(self, machine_id, name, recipes=recipes):
		super().__init__()
		self.inputs = [False, False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]
		self.recipes = recipes

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

class core(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False, False]

	def process(self):
		if self.inputs[0]['material'].isFood:
			self.outflow = [{ 'material': Piss(), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Blood(), 'amount': self.inputs[0]['amount']*0.4}]
			return [{ 'material': Piss(), 'amount': self.inputs[0]['amount']*0.4}, 
				{ 'material': Blood(), 'amount': self.inputs[0]['amount']*0.4}]
		else:
			print('ugh! not food!')
			self.outflow = self.inputs
			return self.inputs

class combi_gate(Machine):
	def __init__(self, machine_id, name):
		super().__init__()
		self.inputs = [False, False]
		self.name = name
		self.machine_id = machine_id
		self.outputs = [False]

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