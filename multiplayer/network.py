from components import *
import components
from app import machine_number, connection_number, log_event, feedback_message, status_message

def machine_num():
	global machine_number
	machine_number +=1
	return machine_number

def connection_num():
	global connection_number
	connection_number +=1
	return connection_number


# redo this function
def get_info(machine_type):
	machineClass = getattr(components, machine_type, None)
	if machineClass is not None:
		temp_machine = machineClass('xx', machine_type)
		header()
		dot_dot()
		print_text(machine_type.title())
		# print('energy cost:', temp_machine.cost)
		print_text('inputs: ' + str(len(temp_machine.inputs)), newline=False)
		print('')
		print_text('outputs: ' + str(len(temp_machine.outputs)), newline=False)
		print('')

		if hasattr(temp_machine, "cost"):
			print_text('cost: ' + str(temp_machine.cost) + ' energy')
		else:
			print_text('You are not currently permitted to purchase this machine')


		print_text('description: ' + temp_machine.description)
		input('[ENTER]')

	else:
		print("couldn't find a machine with this name")

def add_machine(machine_type, machines, player):
	machineClass = getattr(components, machine_type, None)
	print('adding machine of type', machineClass)
	if machineClass is not None:
		new_machine = machineClass(str(machine_num()), machine_type)
		player.update_energy(-new_machine.cost)

		if(player.alive):
			machines.append(new_machine)
			log_event('core ' + player.machine_id + ' added machine ' + new_machine.name)
	else:
		feedback_message('no machine of this type available', player.session_id)

	return machines, player


def add_connection(conn_id, source, dest, voting, machines, connections, player):
	new_conn = components.Connection(source, dest, conn_id, voting)
	cost = new_conn.cost
	if voting: cost = cost + new_conn.vote_cost

	# try drawing the connection
	if new_conn.draw(machines, player):
		if(player.alive):
			player.update_energy(-1*cost)
			connections.append(new_conn)
		else:
			game_over()

	return machines, connections, player

def remove_connection(conn, machines, connections, player):
	machines = conn.remove_conn(machines, player)
	connections.remove(conn)

	return machines, connections


# clear out all the gunk before you recalculate (apart from the inlet node)
def reset_network(machines):
	for node in machines:
		if node.name != "inlet":
			for i, node_in in enumerate(node.inputs):
				node.inputs[i] = False

		else:
			node.inputs = [{'amount': 1.0, 'material': Pellet()}]

		for i, node_out in enumerate(node.outflow):
			node.outflow[i] = False

	return machines

def resolve_network(machines):
		resolved_nodes = []
		counter = 0
		machines = reset_network(machines)

		while len(resolved_nodes) < len(machines):
			for node in machines:
				if False not in node.inputs and node.machine_id not in resolved_nodes:
					resolved_nodes.append(node.machine_id)
					outflows = node.process()

					for i, rx in enumerate(node.outputs):
						if rx != False:
							# propagate temp changes -- inelegant sorry!
							rx_node = next((x for x in machines if x.machine_id == rx), None)

							if rx_node is not None:
								try:
									in_idx = rx_node.inputs.index(False)
									rx_node.inputs[in_idx] = outflows[i]
								except:
									# do we want a feedback message here?
									# print('')
									print('no available inlets for', node.machine_id)

			# if we have to go over the network more than twice the size of the network
			# then we know it's not solvable (is this true?!)
			counter+=1

			if counter == len(machines)*2:
				# print('network currently incomplete. try adding some pipes?')
				break

		return machines