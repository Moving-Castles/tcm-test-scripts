class Material:
	def __init__(self, base_temp):
		self.temp = base_temp

	def heat(self, amount):
		self.temp = self.temp + amount

class Connection():
	def __init__(self, source, dest):
		self.source = source
		self.dest = dest

	def draw(self, machines):
		# check if there's space on the input of source
		# and on the output of dest. if not then 

	def delete(self, machines):
		# remove


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


class Recipe:
	def __init__(self, ingredients, result):
		self.ingredients = ingredients
		self.result = result
# invert_op = getattr(self, "invert_op", None) <- check if method exists on object

class Machine:
	def __init__(self, machine_id, outputs_to, name):
		self.inputs = [False]
		self.name = name

class heater(Machine):
	def __init__(self, machine_id, outputs_to, name):
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		material = self.inputs[0]['material']
		material.name = "hot " + material.name
		return [{'material': material, 'amount': self.inputs[0]['amount']}]

class dryer(Machine):
	def __init__(self, machine_id, outputs_to, name):
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		material = self.inputs[0]['material']
		if getattr(material, "dry", None) is not None:
			material = material.dry()
		else: print('cannot dry')
		return [{'material': material, 'amount': self.inputs[0]['amount']}]

class split_gate(Machine):
	def __init__(self, machine_id, outputs_to, name):
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		return [{ 'amount': self.inputs[0]['amount']/2, 'material': self.inputs[0]['material']}, 
		{ 'amount': self.inputs[0]['amount']/2, 'material': self.inputs[0]['material']}]


class mixer(Machine):
	def __init__(self, machine_id, outputs_to, name):
		self.inputs = [False, False]
		self.name = name
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		ingredients = {self.inputs[1]['material'].name, self.inputs[0]['material'].name}
		result = Dirt()
		for recipe in recipes:
			if recipe.ingredients == ingredients:
				result = recipe.result

		if self.inputs[0]['amount'] > self.inputs[1]['amount']:
			return [{'material': result, 'amount': self.inputs[1]['amount']*2}]

		else:
			return [{'material': result, 'amount': self.inputs[0]['amount']*2}]

class core(Machine):
	def __init__(self, machine_id, outputs_to, name):
		self.inputs = [False]
		self.name = name
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		return [{ 'material': Piss(), 'amount': self.inputs[0]['amount']*0.4}, 
			{ 'material': Blood(), 'amount': self.inputs[0]['amount']*0.4}]

class combi_gate(Machine):
	def __init__(self, machine_id, outputs_to, name):
		self.inputs = [False, False]
		self.name = name
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		print('sent:')
		for out in self.inputs:
			print('  -  ', out['amount'], out['material'].name)

		print('to outlet')
		return self.inputs


class inlet(Machine):
	def __init__(self, machine_id, outputs_to, name):
		self.inputs = [False] #[{'amount': 1.0, 'material': Pellet()}]
		self.name = name
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		return self.inputs


def initialise_machines():
	machines = []

	#add inlet
	machines.append(inlet(0, [1], 'inlet'))
	machines.append(split_gate(1, [2, 3], 'splitter'))
	machines.append(core(2, [5, 6], 'you'))
	machines.append(mixer(3, [4], 'mixer'))
	machines.append(dryer(4, [8], 'dryer'))
	machines.append(split_gate(5, [3, 6], 'splitter'))
	machines.append(mixer(6, [7], 'mixer'))
	machines.append(heater(7, [8], 'heater'))
	machines.append(combi_gate(8, [9], 'combined flow pipe'))

	return machines


def initialise_recipes():
	recipes = []
	recipes.append(Recipe({'piss', 'blood'}, Teeth()))

	return recipes

if __name__ == '__main__':
	machines = initialise_machines()
	recipes = initialise_recipes()


	# each time a machine or connection is added
	# go over the list of connections and 'redraw' the network
	# recalculate input / output

	resolved_nodes = []

	counter = 0
	while len(resolved_nodes) < len(machines):
		for node in machines:
			if False not in node.inputs and node.machine_id not in resolved_nodes:
				resolved_nodes.append(node.machine_id)
				outputs = node.process()

				for i, rx in enumerate(node.outputs_to):
					rx_node = next((x for x in machines if x.machine_id == rx), None)

					if rx_node is not None:
						try:
							in_idx = rx_node.inputs.index(False)
							rx_node.inputs[in_idx] = {
									'amount': outputs[i]['amount'], 
									'material': outputs[i]['material']
								}

							print('sending', outputs[i]['amount'], outputs[i]['material'].name, 'from', node.name, 'to', rx_node.name)
						except:
							print('no available inlets')
					else:
						print('end of network')

		# if we have to go over the network more than twice the size of the network
		# then we know it's not solvable (is this true?!)
		counter+=1

		if counter == len(machines)*2:
			print('no source/sink connection')
			break

			# print('got output from', node.machine_id, outputs)
