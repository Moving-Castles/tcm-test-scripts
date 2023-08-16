from components import *
from materials import *
import components
import os
import sys
from collections import Counter
import time

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


def game_over():
	os.system('clear')
	print("#############################")
	print("YOU DIED!!!!!!!!!!!!!!")
	print("#############################\n")
	time.sleep(2)
	sys.exit()


def print_state():
	os.system('clear')
	print("#############################")
	print("WELCOME TO THIS CURSED MACHINE")
	print("#############################\n")
	print("goal: 10 hot teeth, 20 sand\n")
	print("current world state:\n")

	print("you currently have", player.energy, "energy remaining\n")

	if len(grid_output.pool) !=0:
		print("in your pool there is:")

		for item in grid_output.pool:
			print(item["amount"], item["material"].get_name())

	else:
		print('no materials in pool')

	print("")


	for machine in machines:
		print(machine.name, "with id", machine.machine_id)
		print(" - ", machine.inputs.count(False), "available inputs")
		print(" - ", machine.outputs.count(False), "available outputs")

		for i, inflow in enumerate(machine.inputs):
			if inflow != False:
				print("recieving", inflow["amount"], inflow["material"].get_name(), "on input", i+1)

		for i, output in enumerate(machine.outflow):
			if output != False:
				if output["material"].material_type == "liquid":
					outword = "leaking"
				else:
					outword = "shedding"

				if machine.outputs[i] != False:
					outword = "pumping"

				print(outword, output["amount"], output["material"].get_name(), "from output", i+1)

		print("")

	for connection in connections:
		print("pipe from", connection.source, "to", connection.dest)
	
	print("")


def initialise_grid():
	machines = []

	machines.append(inlet(str(len(machines)), 'inlet'))

	# possibility for second input, hacky for now
	# machines.append(inlet(str(len(machines)), 'inlet'))
	# machines[1].inputs = [{'material': Flesh(), 'amount': 1.0}]
	player = core(str(len(machines)), 'you', 200)
	machines.append(player)

	output = outlet(str(len(machines)), 'outlet')
	machines.append(output)

	return machines, player, output

def add_machine(machine_type):
	machineClass = getattr(components, machine_type)
	if machineClass is not None:
		new_machine = machineClass(str(len(machines)), machine_type)
		player.update_energy(-new_machine.cost)

		if(player.alive):
			machines.append(new_machine)

		else:
			game_over()
	else:
		print('no machine of this type avaible')


def add_connection(source, dest):
	new_conn = Connection(source, dest)
	player.update_energy(-new_conn.cost)
	
	if(player.alive):
		new_conn.draw(machines)
		connections.append(new_conn)

	else:
		game_over()

# clear out all the gunk before you recalculate (apart from the inlet node)
def reset_network():
	for node in machines:
		if node.name != "inlet":
			for i, node_in in enumerate(node.inputs):
				node.inputs[i] = False

def resolve_network():
		resolved_nodes = []
		counter = 0
		reset_network()

		while len(resolved_nodes) < len(machines):
			for node in machines:
				if False not in node.inputs and node.machine_id not in resolved_nodes:
					resolved_nodes.append(node.machine_id)
					outputs = node.process()

					for i, rx in enumerate(node.outputs):
						if rx != False:
							rx_node = next((x for x in machines if x.machine_id == rx), None)

							if rx_node is not None:
								try:
									in_idx = rx_node.inputs.index(False)
									rx_node.inputs[in_idx] = outputs[i]
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
	machines, player, grid_output = initialise_grid()
	connections = []

	os.system('clear')
	time.sleep(0.2)
	print("################################")
	print("INTELLIGENT LEARNING ENVIRONMENT")
	print("################################\n")
	# time.sleep(1)

	print("loading goal", end='')
	for i in range(0, 10):
		print(".", end='', flush=True)
		time.sleep(0.1)

	# time.sleep(1)
	os.system('clear')
	print("#############################")
	print("WELCOME TO THIS CURSED MACHINE")
	print("#############################\n")
	print("goal: 10 hot teeth, 20 sand\n")

	# each time a machine or connection is added
	# go over the list of connections and 'redraw' the network
	# recalculate input / output

	print("initialising world", end='')
	for i in range(0, 10):
		print(".", end='', flush=True)
		time.sleep(0.1)


	while True:
		resolve_network()
		print_state()

		opt = input('to add a machine type [m]. to link a pipe, type [p]. To do nothing, press any other key. \n> ')

		if opt == "m":
			# print("available machines: [heater, mixer, dryer, split_gate]")
			new_machine = input('name of new machine (choose from [splitter, scorcher, blender, parcher]): \n> ')
			add_machine(new_machine)

		elif opt == "p":
			source = input('source machine id: ')
			dest = input('target machine id: ')
			add_connection(source, dest)


				# print('got output from', node.machine_id, outputs)
