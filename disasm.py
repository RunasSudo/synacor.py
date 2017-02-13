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

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file', help='.bin file containing the initial memory dump')
parser.add_argument('--hints', help='File(s) outlining additional jmp/call targets, label names, comments, etc', action='append')
args = parser.parse_args()

with open(args.file, 'rb') as data:
	SYN_MEM = memory_from_file(data)

# Find things to label
labels, comments_before, comments_inline, replacements = {}, {}, {}, {}
SYN_PTR = 0
while SYN_PTR < len(SYN_MEM):
	word = SYN_MEM[SYN_PTR]
	if word in instructions_by_opcode:
		instruction, SYN_PTR = Instruction.next_instruction(SYN_MEM, SYN_PTR)
		if isinstance(instruction, InstructionJmp) or isinstance(instruction, InstructionJt) or isinstance(instruction, InstructionJf):
			if isinstance(instruction, InstructionJmp):
				op = instruction.args[0]
			else:
				op = instruction.args[1]
			if isinstance(op, OpLiteral):
				loc = op.get(None)
				labels['label_{:04x}'.format(loc)] = loc
		elif isinstance(instruction, InstructionCall):
			if isinstance(instruction.args[0], OpLiteral):
				loc = instruction.args[0].get(None)
				labels['sub_{:04x}'.format(loc)] = loc
	else:
		SYN_PTR += 1
# Read hints
if args.hints:
	for hintfile in args.hints:
		with open(hintfile, 'r') as data:
			while True:
				line = data.readline()
				if line == '':
					break
				if line.startswith('jmp '):
					loc = int(line.split()[1], 16)
					labels['label_{:04x}'.format(loc)] = loc
				elif line.startswith('call '):
					loc = int(line.split()[1], 16)
					labels['sub_{:04x}'.format(loc)] = loc
				elif line.startswith('lbl '):
					loc = int(line.split()[1], 16)
					labels[line.split()[2]] = loc
				elif line.startswith('ren '):
					old_label = line.split()[1]
					new_label = line.split()[2]
					labels[new_label] = labels[old_label]
					del labels[old_label]
				elif line.startswith('cmb '):
					loc = int(line.split()[1], 16)
					comment = line[line.index(' ', line.index(' ') + 1) + 1:].strip()
					if loc not in comments_before:
						comments_before[loc] = []
					comments_before[loc].append(comment)
				elif line.startswith('cmi '):
					loc = int(line.split()[1], 16)
					comment = line[line.index(' ', line.index(' ') + 1) + 1:].strip()
					comments_inline[loc] = comment
				elif line.startswith('rep '):
					loc = int(line.split()[1], 16)
					code = line[line.index(' ', line.index(' ') + 1) + 1:].strip()
					instruction = assemble_line(None, code)[0][0]
					replacements[loc] = instruction
				else:
					raise Exception('Invalid line in hint file: {}'.format(line))

MODE_OUT = False
MODE_DAT = False #False, 1 (data), 2 (text)

SYN_PTR = 0

while SYN_PTR < len(SYN_MEM):
	# Handle comments
	if SYN_PTR in comments_before:
		if MODE_OUT:
			print('"')
			MODE_OUT = False
		if MODE_DAT == 1:
			print()
			MODE_DAT = False
		if MODE_DAT == 2:
			print('"')
			MODE_DAT = False
		for comment in comments_before[SYN_PTR]:
			print('; {}'.format(comment))
	if SYN_PTR in comments_inline:
		comment_inline = ' ; {}'.format(comments_inline[SYN_PTR])
	else:
		comment_inline = ''
	
	# Handle labels
	if any(v == SYN_PTR for k, v in labels.items()):
		if MODE_OUT:
			print('"')
			MODE_OUT = False
		if MODE_DAT == 1:
			print()
			MODE_DAT = False
		if MODE_DAT == 2:
			print('"')
			MODE_DAT = False
		print('${}:'.format(next(k for k, v in labels.items() if v == SYN_PTR)))
	
	# Handle replacements
	if SYN_PTR in replacements:
		instruction = replacements[SYN_PTR]
		print('{:04x}: {}{}'.format(SYN_PTR, instruction.describe(), comment_inline))
		SYN_PTR += len(instruction.assemble(None))
		continue
	
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
		instruction, next_SYN_PTR = Instruction.next_instruction(SYN_MEM, SYN_PTR)
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
				print('{:04x}: {}{}'.format(SYN_PTR, instruction.describe(), comment_inline))
		elif isinstance(instruction, InstructionJmp) or isinstance(instruction, InstructionJt) or isinstance(instruction, InstructionJf) or isinstance(instruction, InstructionCall):
			if isinstance(instruction, InstructionJmp) or isinstance(instruction, InstructionCall):
				argidx = 0
			else:
				argidx = 1
			if isinstance(instruction.args[argidx], OpLiteral):
				loc = instruction.args[argidx].get(None)
				if any(v == loc for k, v in labels.items()):
					label = next(k for k, v in labels.items() if v == loc)
					instruction.args[argidx] = OpLabel(label)
			print('{:04x}: {}{}'.format(SYN_PTR, instruction.describe(), comment_inline))
		else:
			print('{:04x}: {}{}'.format(SYN_PTR, instruction.describe(), comment_inline))
		SYN_PTR = next_SYN_PTR
