class Machine:
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False]

class heater(Machine):
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False]
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		return self.inputs

class dryer(Machine):
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False]
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		return self.inputs

class split_gate(Machine):
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False]
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		return [self.inputs[0]/2, self.inputs[0]/2]

class mixer(Machine):
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False, False]
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		if self.inputs[0] > self.inputs[1]:
			return [self.inputs[1]*2]

		else:
			return [self.inputs[0]*2]

class core(Machine):
	def __init__(self, machine_id, outputs_to):
		self.inputs = [False]
		self.machine_id = machine_id
		self.outputs_to = outputs_to

	def process(self):
		return [self.inputs[0]*0.4, self.inputs[0]*0.4]

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
		self.inputs = [1.0]
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


if __name__ == '__main__':
	network = initialise_network()
	resolved_nodes = []

	while len(resolved_nodes) < len(network):
		for node in network:
			if False not in node.inputs:
				if node.machine_id not in resolved_nodes: 
					resolved_nodes.append(node.machine_id)

				outputs = node.process()
				for i, rx in enumerate(node.outputs_to):
					print('rx is', rx)
					rx_node = next((x for x in network if x.machine_id == rx), None)

					if rx_node is not None:
						try:
							rx_node.inputs[rx_node.inputs.index(False)] = outputs[i]
							print('set input of', rx, 'to', rx_node.inputs)
						except:
							print('no available inlets')
						# next((inlet for inlet in rx_node.inputs if inlet == False), None)
					else:
						print('end of network')



			print('got output from', node.machine_id, outputs)

# main_input = 1.0
# output = combi_gate([mixer([split_gate(main_input)[1], split_gate(core(split_gate(main_input)[0])[0])[1]]), heater(mixer([core(split_gate(main_input)[0])[1], split_gate(core(split_gate(main_input)[0])[0])[0]]))])

# algorithm:
# work backward from the output to get the input?

# or -- work through and check if inputs in list, if not go to next linked node


# b = split_gate(main_input)[0]
# f = split_gate(main_input)[1]
# print(output)

