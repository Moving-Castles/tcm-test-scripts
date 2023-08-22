# define ports on machines
# define connections on sources
# define functions on machines
# profit?
import uuid

class Machine:
	def __init__(self, name, inputs, outputs):
		self.name=name
		self.efficiency = 1
		self.inputs = inputs
		self.outputs = outputs
		self.output_multiplier = len(inputs) / len(outputs)

class Organ:
	def __init__(self, name, efficiency):
		self.name=name
		self.efficiency = efficiency

class Port:
	def __init__(self):
		self.id = uuid.uuid4()

class Input(Port):
	def __init__(self, material='', amount=0):
		Port.__init__(self)
		self.material = material
		self.amount = amount

class Output(Port):
	def __init__(self, port_id, material='', amount=0):
		Port.__init__(self)
		self.material = material
		self.amount = amount

class Connection():
	def __init__(self, source, dest):
		self.source = source #port
		self.dest = dest #port

class Split_Gate(Machine):
	def __init__(self, [input_0], [output_0, output_1]):
		Machine.__init__(self, 'split_gate', [input_0], [output_0, output_1])
		self.cost = 5

	def process():
		self.outputs[0].material = self.inputs[0].material
		self.outputs[1].material = self.inputs[0].material
		self.outputs[0].amount = self.inputs[0].amount*self.output_multiplier
		self.outputs[1].amount = self.inputs[0].amount*self.output_multiplier

class Inflow_Pipe(Machine):
	def __init__(self, output)
		Machine.__init__(self, 'inflow_pipe')
		self.cost = 5

	def process():

class Heater(Machine):
	def __init__(self, [input], [output]):
		Machine.__init__(self, 'heater')
		self.cost = 5

	def process():

class Core(Organ):
	def __init__(self, [input], [output_0, output_1]):
		Organ.__init__(self, 'core', 0.8)
		self.cost = 0

	def process():


class Dryer(Machine):
	def __init__(self, [input], [output]):
		Machine.__init__(self, 'dryer')
		self.cost = 5


machines = []