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
parser.add_argument('--smart', help='Given a raw Synacor challenge file, disassemble in a Synacor-aware manner', action='store_true')
parser.add_argument('--aggressive-labels', help='Replace values with corresponding labels irrespective of where they appear', action='store_true')
args = parser.parse_args()

with open(args.file, 'rb') as data:
	SYN_MEM = memory_from_file(data)
	disassemble_end = len(SYN_MEM)

labels, comments_before, comments_inline, replacements = {}, {}, {}, {}

# Do smart things if requested
if args.smart:
	disassemble_end = 0x17b4
	# Emulate 06bb to decrypt data
	for R1 in range(disassemble_end, 0x7562):
		R0 = SYN_MEM[R1]
		R0 ^= pow(R1, 2, 32768)
		R0 ^= 0x4154
		SYN_MEM[R1] = R0

# Find things to label
SYN_PTR = 0
while SYN_PTR < disassemble_end:
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

def set_mode_out(mode):
	global MODE_OUT
	if MODE_OUT == mode:
		pass
	elif mode == False:
		# Switching off
		print('"')
	else:
		# Switching on
		print('{:04x}: out  "'.format(SYN_PTR), end='')
	MODE_OUT = mode
def set_mode_dat(mode):
	global MODE_DAT
	if MODE_DAT == mode:
		pass
	elif mode == False:
		# Switching off
		if MODE_DAT == 2:
			print('"', end='')
		print()
	elif MODE_DAT == 1:
		# Switching from data to text
		print()
		print('{:04x}: data "'.format(SYN_PTR), end='')
	elif MODE_DAT == 2:
		# Switching from text to data
		print('"')
		print('{:04x}: data'.format(SYN_PTR), end='')
	else:
		# Switching to a new mode
		print('{:04x}: data'.format(SYN_PTR), end='')
		if mode == 2:
			print('"', end='')
	MODE_DAT = mode
def clear_modes():
	set_mode_out(False)
	set_mode_dat(False)

while SYN_PTR < len(SYN_MEM):
	# Handle comments
	if SYN_PTR in comments_before:
		clear_modes()
		for comment in comments_before[SYN_PTR]:
			print('; {}'.format(comment))
	if SYN_PTR in comments_inline:
		comment_inline = ' ; {}'.format(comments_inline[SYN_PTR])
	else:
		comment_inline = ''
	
	# Handle labels
	if any(v == SYN_PTR for k, v in labels.items()):
		clear_modes()
		print('${}:'.format(next(k for k, v in labels.items() if v == SYN_PTR)))
	
	# Handle replacements
	if SYN_PTR in replacements:
		instruction = replacements[SYN_PTR]
		print('{:04x}: {}{}'.format(SYN_PTR, instruction.describe(), comment_inline))
		SYN_PTR += len(instruction.assemble(None))
		continue
	
	word = SYN_MEM[SYN_PTR]
	
	if SYN_PTR >= disassemble_end or word not in instructions_by_opcode:
		# Data
		if 32 <= word <= 126:
			# Looks like letters - unfortunately "\n" looks like MULT
			set_mode_dat(2)
			print(escape_char(chr(word)), end='')
			if word == 0x0a:
				clear_modes() # Break on newlines
		else:
			set_mode_dat(1)
			print(' {:04x}'.format(word), end='')
		SYN_PTR += 1
	else:
		# Instruction
		instruction, next_SYN_PTR = Instruction.next_instruction(SYN_MEM, SYN_PTR)
		# Special cases
		if isinstance(instruction, InstructionOut):
			if isinstance(instruction.args[0], OpLiteral):
				set_mode_out(True)
				print(escape_char(chr(instruction.args[0].get(None))), end='')
				if instruction.args[0].get(None) == 0x0a:
					clear_modes() # Break on newlines
			else:
				clear_modes()
				print('{:04x}: {}{}'.format(SYN_PTR, instruction.describe(), comment_inline))
		elif isinstance(instruction, InstructionJmp) or isinstance(instruction, InstructionJt) or isinstance(instruction, InstructionJf) or isinstance(instruction, InstructionCall):
			clear_modes()
			if isinstance(instruction, InstructionJmp) or isinstance(instruction, InstructionCall):
				argidx = 0
			else:
				argidx = 1
			# Aggressively replace labels if requested
			for argnum in range(instruction.nargs) if args.aggressive_labels else [argidx]:
				if isinstance(instruction.args[argnum], OpLiteral):
					loc = instruction.args[argnum].get(None)
					if any(v == loc for k, v in labels.items()):
						label = next(k for k, v in labels.items() if v == loc)
						instruction.args[argnum] = OpLabel(label)
			print('{:04x}: {}{}'.format(SYN_PTR, instruction.describe(), comment_inline))
		else:
			# Aggressively replace labels if requested
			if args.aggressive_labels:
				for argnum in range(instruction.nargs):
					if isinstance(instruction.args[argnum], OpLiteral):
						loc = instruction.args[argnum].get(None)
						if any(v == loc for k, v in labels.items()):
							label = next(k for k, v in labels.items() if v == loc)
							instruction.args[argnum] = OpLabel(label)
			clear_modes()
			print('{:04x}: {}{}'.format(SYN_PTR, instruction.describe(), comment_inline))
		SYN_PTR = next_SYN_PTR
