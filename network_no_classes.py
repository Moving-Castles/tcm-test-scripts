def heater(input_0):
	return input_0

def dryer(input_0):
	return input_0

def split_gate(input_0):
	return [input_0/2, input_0/2]

def mixer(inputs):
	if inputs[0] > inputs[1]:
		return inputs[1]*2

	else:
		return inputs[0]*2

def core(input_0):
	return [input_0*0.4, input_0*0.4]

def combi_gate(inputs):
	return inputs


main_input = 1.0
output = combi_gate([mixer([split_gate(main_input)[1], split_gate(core(split_gate(main_input)[0])[0])[1]]), heater(mixer([core(split_gate(main_input)[0])[1], split_gate(core(split_gate(main_input)[0])[0])[0]]))])

# b = split_gate(main_input)[0]
# f = split_gate(main_input)[1]
print(output)

