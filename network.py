from components import *
from materials import *
import components
import os

def initialise_machines_full():
	machines = []
	connections = []

	#add inlet
	machines.append(inlet(0, 'inlet'))
	machines.append(split_gate(1, 'splitter'))
	machines.append(core(2, 'you'))
	machines.append(mixer(3, 'mixer'))
	machines.append(dryer(4, 'dryer'))
	machines.append(split_gate(5,'splitter'))
	machines.append(mixer(6, 'mixer'))
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

def print_state():
	# print(machines)
	os.system('clear')
	print("#############################")
	print("WELCOME TO THIS CURSED MACHINE")
	print("#############################\n")
	print("goal: 10 hot teeth, 20 sand\n")
	print("current world state:\n")

	for machine in machines:
		print(machine.name, "with id", machine.machine_id)
		print(" - ", len(machine.inputs), "available inputs")
		print(" - ", len(machine.outputs), "available outputs")

		for i, inflow in enumerate(machine.inputs):
			if inflow != False:
				print("recieving", inflow["amount"], inflow["material"].name, "on input", i+1)

		for i, output in enumerate(machine.outflow):
			if output != False:
				print("leaking", output["amount"], output["material"].name, "from output", i+1)

		print("")

	for connection in connections:
		print("connection from", connection.source, "to", connection.dest)
		print("")


def initialise_grid():
	machines = []

	machines.append(inlet(str(len(machines)), 'inlet'))
	machines.append(core(str(len(machines)), 'you'))

	return machines

def add_machine(machine_type):
	print(machines)
	machineClass = getattr(components, machine_type)
	if machineClass is not None:
		machines.append(machineClass(str(len(machines)), machine_type))
	else:
		print('no machine of this type avaible')


def resolve_network():
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

								# print('sending', outputs[i]['amount'], outputs[i]['material'].name, 'from', node.name, 'to', rx_node.name)
							except:
								print('no available inlets for', node.machine_id)

			# if we have to go over the network more than twice the size of the network
			# then we know it's not solvable (is this true?!)
			counter+=1

			if counter == len(machines)*2:
				print('no source/sink connection')
				break

if __name__ == '__main__':
	# machines, connections = initialise_machines_full()
	machines = initialise_grid()
	connections = []

	# each time a machine or connection is added
	# go over the list of connections and 'redraw' the network
	# recalculate input / output

	while True:
		resolve_network()
		print_state()

		opt = input('to add a machine press [1]. to make a connection, press [2]. to run simulation, press [3] \n> ')

		if opt == "1":
			new_machine = input('name of new machine \n> ')
			add_machine(new_machine)

		elif opt == "2":
			source = input('id of machine for source of connection \n> ')
			dest = input('id of machine for destination of connection \n> ')
			new_conn = Connection(source, dest)
			new_conn.draw(machines)

			connections.append(new_conn)

		elif opt == "3":
			break

		else:
			print("invalid input, try again")


				# print('got output from', node.machine_id, outputs)
