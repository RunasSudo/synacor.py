#!/usr/bin/env python3
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

import sys

with open(sys.argv[1], 'rb') as data:
	SYN_MEM = memory_from_file(data)

def escape_char(char):
	return char.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')

MODE_OUT = False
MODE_DAT = False #False, 1 (data), 2 (text)

SYN_PTR = 0

while SYN_PTR < len(SYN_MEM):
	word = SYN_MEM[SYN_PTR]
	
	if MODE_OUT and word != 19:
		print('"')
		MODE_OUT = False
	if MODE_DAT and 0 <= word <= 21:
		if MODE_DAT == 1:
			print()
		if MODE_DAT == 2:
			print('"')
		MODE_DAT = False
	
	if word not in instructions_by_opcode:
		# Data
		if 32 <= word <= 126:
			# looks like letters - unfortunately "\n" looks like MULT
			if MODE_DAT == 2:
				print(escape_char(chr(word)), end='')
			else:
				if MODE_DAT == 1:
					print()
				print('{:04x}: data "{}'.format(SYN_PTR, escape_char(chr(word))), end='')
				MODE_DAT = 2
			if word == 0x0a:
				print('"')
				MODE_DAT = False # break on newlines
		else:
			if MODE_DAT == 1:
				print(' {:04x}'.format(word), end='')
			else:
				if MODE_DAT == 2:
					print('"')
				print('{:04x}: data {:04x}'.format(SYN_PTR, word), end='')
				MODE_DAT = 1
		SYN_PTR += 1
	else:
		# Instruction
		instruction, SYN_PTR = Instruction.next_instruction(SYN_MEM, SYN_PTR)
		# Special cases
		if isinstance(instruction, InstructionOut):
			if isinstance(instruction.args[0], OpLiteral):
				if MODE_OUT:
					print(escape_char(chr(instruction.args[0].get(None))), end='')
				else:
					print('{:04x}: out  "{}'.format(SYN_PTR, escape_char(chr(instruction.args[0].get(None)))), end='')
					MODE_OUT = True
				if instruction.args[0].get(None) == 0x0a:
					print('"')
					MODE_OUT = False # break on newlines
			else:
				if MODE_OUT:
					print('"')
					MODE_OUT = False
				print('{:04x}: {}'.format(SYN_PTR, instruction.describe()))
		else:
			print('{:04x}: {}'.format(SYN_PTR, instruction.describe()))
