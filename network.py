from components import *
from materials import *

def initialise_machines():
	machines = []
	connections = []

	#add inlet
	machines.append(inlet(0, 'inlet'))
	machines.append(split_gate(1, 'splitter'))
	machines.append(core(2, 'you'))
	machines.append(mixer(3, 'mixer', recipes))
	machines.append(dryer(4, 'dryer'))
	machines.append(split_gate(5,'splitter'))
	machines.append(mixer(6, 'mixer', recipes))
	machines.append(heater(7, 'heater'))
	machines.append(combi_gate(8, 'combined flow pipe'))

	connections.append(Connection(0, 1))
	connections.append(Connection(1, 2))
	connections.append(Connection(1, 3))
	connections.append(Connection(2, 5))
	connections.append(Connection(2, 6))
	connections.append(Connection(3, 4))
	connections.append(Connection(4, 8))
	connections.append(Connection(5, 3))
	connections.append(Connection(5, 6))
	connections.append(Connection(6, 7))
	connections.append(Connection(7, 8))
	connections.append(Connection(8, 9))

	for conn in connections:
		conn.draw(machines)

	return machines, connections


def initialise_recipes():
	recipes = []
	recipes.append(Recipe({'piss', 'blood'}, Teeth()))

	return recipes

if __name__ == '__main__':
	recipes = initialise_recipes()
	machines, connections = initialise_machines()

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

				for i, rx in enumerate(node.outputs):
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
