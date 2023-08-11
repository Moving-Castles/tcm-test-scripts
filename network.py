class Material:
	def __init__(self, base_temp):
		self.temp = base_temp

	def heat(self, amount):
		self.temp = self.temp + amount


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


# class Recipe:
# 	def __init__(self, ingredients, result)
# invert_op = getattr(self, "invert_op", None) <- check if method exists on object

class Machine:
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False]

class heater(Machine):
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False]
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		material = self.inputs[0]['material']
		material.name = "hot " + material.name
		return [{'material': material, 'amount': self.inputs[0]['amount']}]

class dryer(Machine):
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False]
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		material = self.inputs[0]['material']
		if getattr(material, "dry", None) is not None:
			material = material.dry()
		else: print('cannot dry')
		return [{'material': material, 'amount': self.inputs[0]['amount']}]

class split_gate(Machine):
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False]
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		return [{ 'amount': self.inputs[0]['amount']/2, 'material': self.inputs[0]['material']}, 
		{ 'amount': self.inputs[0]['amount']/2, 'material': self.inputs[0]['material']}]


class mixer(Machine):
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False, False]
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		if self.inputs[0]['amount'] > self.inputs[1]['amount']:
			return [{'material': self.inputs[1]['material'], 'amount': self.inputs[1]['amount']*2}]

		else:
			return [{'material': self.inputs[0]['material'], 'amount': self.inputs[0]['amount']*2}]

class core(Machine):
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False]
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		return [{ 'material': Piss(), 'amount': self.inputs[0]['amount']*0.4}, 
			{ 'material': Blood(), 'amount': self.inputs[0]['amount']*0.4}]

class combi_gate(Machine):
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False, False]
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		print('sent', self.inputs, 'to outlet')
		return self.inputs


class inlet(Machine):
	def __init__(self, machine_id, outputs_to):
		self.inputs = [{'amount': 1.0, 'material': Pellet()}]
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		return self.inputs


def initialise_network():
	network = []

	#add inlet
	network.append(inlet(0, [1]))
	network.append(split_gate(1, [2, 3]))
	network.append(core(2, [5, 6]))
	network.append(mixer(3, [4]))
	network.append(dryer(4, [8]))
	network.append(split_gate(5, [3, 6]))
	network.append(mixer(6, [7]))
	network.append(heater(7, [8]))
	network.append(combi_gate(8, [9]))

	return network


def initialise_recipes():
	recipes = []


	return recipes

if __name__ == '__main__':
	network = initialise_network()
	resolved_nodes = []

	while len(resolved_nodes) < len(network):
		for node in network:
			if False not in node.inputs and node.machine_id not in resolved_nodes:
				print('node inputs are', node.inputs)
				resolved_nodes.append(node.machine_id)
				outputs = node.process()

				for i, rx in enumerate(node.outputs_to):
					print('rx is', rx)
					rx_node = next((x for x in network if x.machine_id == rx), None)

					if rx_node is not None:
						try:
							rx_node.inputs[rx_node.inputs.index(False)] = {
									'amount': outputs[i]['amount'], 
									'material': outputs[i]['material']
								}

							print('set input of', rx, 'to', rx_node.inputs)
						except:
							print('no available inlets')
					else:
						print('end of network')


			# print('got output from', node.machine_id, outputs)
