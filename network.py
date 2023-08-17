from components import *
from materials import *
import components
import os
import sys
from collections import Counter
import time

debug_mode = False
messages = []

def feedback_message(message):
	messages.append(message)

def dot_dot(length=10):
	for i in range(0, length):
		print(".", end='', flush=True)
		time.sleep(0.1)


def victory():
	if not debug_mode: os.system('clear')
	print("#############################")
	print("YOU WON!!!!!!!!!!!!!!")
	print("#############################\n")
	time.sleep(2)
	sys.exit()


def game_over():
	if not debug_mode: os.system('clear')
	print("#############################")
	print("YOU DIED!!!!!!!!!!!!!!")
	print("#############################\n")
	time.sleep(2)
	sys.exit()


def is_in_cycle(machine_id, visited, recursion_stack):
	nxt = visited.index(False)
	visited[nxt] = machine_id
	nxt_2 = recursion_stack.index(False)
	recursion_stack[nxt_2] = machine_id

	links = list(filter(lambda c: c.source == machine_id, connections))

	for link in links:
		# if we get back to where we came from in the same loop
		if link.dest not in visited:
			if is_in_cycle(link.dest, visited, recursion_stack):
				return True
		elif link.dest in recursion_stack:
				return True

	recursion_stack[nxt_2] = False
	return False

# if there's a cycle and it's still valid replace cycle w/ pseudomachine
def detect_cycles():
	visited = [False]*len(machines)
	recursion_stack = [False]*len(machines)

	for machine in machines:
		if machine.machine_id not in visited:
			if is_in_cycle(machine.machine_id, visited, recursion_stack):
				if not debug_mode: os.system('clear')
				print('feedback cycle detected', end='')
				dot_dot()
				print('system overload', end='')
				dot_dot()
				player.die()
				game_over()

def print_messages():
	global messages
	if not debug_mode: os.system('clear')
	for message in messages:
		print(message)
		time.sleep(0.2)

	# reset every time
	messages = []
	dot_dot()

def print_state():
	if not debug_mode: os.system('clear')
	print("#############################")
	print("WELCOME TO THIS CURSED MACHINE")
	print("#############################\n")
	print('goal:')
	for material in win_state:
		print(material['amount'], material['material_name'])
	print('')

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
		print("pipe from", connection.source, "to", connection.dest, "with id", connection.conn_id)
	
	print("")

def check_win_state():
	global win_state

	for win_material in win_state:
		pool_material = next((o for o in grid_output.pool if o['material'].get_name() == win_material['material_name']), None)
		if pool_material is not None:
			if pool_material['amount'] >= win_material['amount']:
				feedback_message('you got enough ' + win_material['material_name'] + '!')
				win_state.remove(win_material)

	if len(win_state) == 0:
		print_messages()
		victory()

def initialise_grid():
	machines = []

	machines.append(inlet(str(len(machines)), 'inlet'))

	# possibility for second input, hacky for now
	# machines.append(inlet(str(len(machines)), 'inlet'))
	# machines[1].inputs = [{'material': Flesh(), 'amount': 1.0}]
	player = core(str(len(machines)), 'you', 300)
	machines.append(player)

	output = outlet(str(len(machines)), 'outlet')
	machines.append(output)

	return machines, player, output

def add_machine(machine_type):
	machineClass = getattr(components, machine_type, None)
	if machineClass is not None:
		new_machine = machineClass(str(len(machines)), machine_type)
		player.update_energy(-new_machine.cost)

		if(player.alive):
			machines.append(new_machine)

		else:
			game_over()
	else:
		feedback_message('no machine of this type available')

# I think this has to also remove all the connections
def remove_machine(machine_id):
	machine = next((x for x in machines if x.machine_id == machine_id), None)
	if machine is not None:
		if getattr(machine, "remove_machine", None) is not None:
			machine.remove_machine
		if machine.can_remove: machines.remove(machine)
		for connection in connections:
			if connection.source == machine_id or connection.dest == machine_id:
				remove_connection(connection.conn_id)
	else:
		feedback_message('no machine with this id to remove')


def add_connection(source, dest):
	new_conn = Connection(source, dest, str(len(connections)))
	player.update_energy(-new_conn.cost)
	
	if(player.alive):
		new_conn.draw(machines)
		connections.append(new_conn)

	else:
		game_over()

def remove_connection(conn_id):
	conn = next((x for x in connections if x.conn_id == conn_id), None)
	if conn is not None:
		conn.remove_conn(machines)
		connections.remove(conn)
	else:
		feedback_message('no connection with this id to remove')


# clear out all the gunk before you recalculate (apart from the inlet node)
def reset_network():
	for node in machines:
		if node.name != "inlet":
			for i, node_in in enumerate(node.inputs):
				node.inputs[i] = False

		for i, node_out in enumerate(node.outflow):
			node.outflow[i] = False

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
									# do we want a feedback message here?
									print('')
									# print('no available inlets for', node.machine_id)

			# if we have to go over the network more than twice the size of the network
			# then we know it's not solvable (is this true?!)
			counter+=1

			if counter == len(machines)*2:
				# feedback_message('network currently incomplete. try adding some pipes?')
				break

if __name__ == '__main__':
	# machines, connections = initialise_machines_full()
	machines, player, grid_output = initialise_grid()
	connections = []
	win_state = [{
		'material_name': 'hot teeth',
		'amount': 10,
		'done': False
	},
	{
		'material_name': 'sand',
		'amount': 20,
		'done': False
	}]

	os.system('clear')
	time.sleep(0.2)
	print("################################")
	print("WELCOME TO THIS CURSED MACHINE")
	print("################################\n")
	# time.sleep(1)

	print("loading goal", end='')
	dot_dot()

	# time.sleep(1)
	os.system('clear')
	print("################################")
	print("WELCOME TO THIS CURSED MACHINE")
	print("################################\n")
	print('goal:')
	for material in win_state:
		print(material['amount'], material['material_name'])
	print('')

	# each time a machine or connection is added
	# go over the list of connections and 'redraw' the network
	# recalculate input / output

	print("initialising world", end='')
	dot_dot()


	while True:
		detect_cycles()
		resolve_network()
		check_win_state()
		if len(messages) > 0: print_messages()
		print_state()

		opt = input('To add a machine type [m]. to link a pipe, type [p].\nTo remove a machine, type [rm] and to remove a pipe, type [rp].\nTo do nothing, press any other key. \n> ')

		if opt == "m":
			# print("available machines: [heater, mixer, dryer, split_gate]")
			new_machine = input('name of new machine (choose from [splitter, scorcher, blender, parcher]): \n> ')
			add_machine(new_machine)

		elif opt == "p":
			source = input('source machine id: ')
			dest = input('target machine id: ')
			add_connection(source, dest)

		elif opt == "rm":
			rm = input('enter the id of the machine you would like to remove: ')
			remove_machine(rm)

		elif opt == "rp":
			rp = input('enter the id of the pipe you would like to remove: ')
			remove_connection(rp)


				# print('got output from', node.machine_id, outputs)
