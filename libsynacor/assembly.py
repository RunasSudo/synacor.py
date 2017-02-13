#    synacor.py - An implementation of the Synacor Challenge
#    Copyright © 2017  RunasSudo
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from libsynacor import *

def escape_char(char):
	return char.encode('unicode_escape').decode('utf-8').replace('"', '\\"')

def unescape_char(char):
	return char.encode('utf-8').decode('unicode_escape')

def split_line(line):
	tokens = []
	token = ''
	idx = 0
	
	in_comment = False
	in_string = False
	in_escape = False
	
	while idx < len(line):
		if in_comment:
			pass
		elif in_string:
			if in_escape:
				token += line[idx]
			else:
				if line[idx] == '\\':
					in_escape = True
					token += line[idx]
				elif line[idx] == '"':
					in_string = False
					token += line[idx]
				else:
					token += line[idx]
		else:
			if line[idx] == ' ':
				if token != '':
					tokens.append(token)
				token = ''
			elif line[idx] == '"':
				in_string = True
				token += line[idx]
			elif line[idx] == ';':
				in_comment = True
			else:
				token += line[idx]
		idx += 1
	# Final token
	if token != '':
		tokens.append(token)
	
	return tokens

line_no = 0

def assemble_next_instruction(source):
	line = source.readline()
	global line_no; line_no += 1
	if line == '':
		return None, []
	
	return assemble_line(source, line)

def assemble_line(source, line):
	tokens = split_line(line.strip())
	return assemble_instruction(source, tokens)

def assemble_instruction(source, tokens):
	if len(tokens) == 0:
		return assemble_next_instruction(source)
	if tokens[0].endswith(':'):
		# Label
		label = tokens[0][:-1]
		instructions, inst_labels = assemble_instruction(source, tokens[1:])
		return instructions, inst_labels + [label]
	else:
		# Instruction
		name = tokens[0]
		if name not in instructions_by_name:
			raise Exception('Unknown instruction {}'.format(name))
		instruction = instructions_by_name[name]()
		
		# Special cases
		if isinstance(instruction, InstructionOut) and tokens[1].startswith('"'):
			chars = unescape_char(tokens[1][1:-1])
			instructions = []
			for char in chars:
				instruction = InstructionOut()
				instruction.args.append(OpLiteral(ord(char)))
				instructions.append(instruction)
			return instructions, []
		elif isinstance(instruction, InstructionData):
			if tokens[1].startswith('"'):
				chars = unescape_char(tokens[1][1:-1])
				instruction.args = [ord(char) for char in chars]
				return [instruction], []
			else:
				instruction.args = [int(x, 16) for x in tokens[1:]]
				return [instruction], []
		else:
			if len(tokens) != instruction.nargs + 1:
				raise Exception('Invalid number of arguments: Expected {}, got {}'.format(instruction.nargs, len(tokens) - 1))
			for i in range(instruction.nargs):
				argstr = tokens[i + 1]
				if argstr.startswith('R'):
					# Register
					arg = OpRegister(int(argstr[1:]))
				elif argstr.startswith('$'):
					# Label
					arg = OpLabel(argstr[1:])
				else:
					# Hex literal
					arg = OpLiteral(int(argstr, 16))
				instruction.args.append(arg)
			return [instruction], []
