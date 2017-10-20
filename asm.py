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
import struct

parser = argparse.ArgumentParser()
parser.add_argument('file', help='.asm file to read')
parser.add_argument('output', help='.bin file to write')
args = parser.parse_args()

# First pass
labels = {}
SYN_MEM = [0] * 32768
SYN_PTR = 0

with open(args.file, 'r') as source:
	try:
		while True:
			instructions, inst_labels = assemble_next_instruction(source)
			for label in inst_labels:
				if label.startswith('$'):
					labels[label[1:]] = SYN_PTR
			if instructions is None:
				break
			for instruction in instructions:
				code = instruction.assemble(None)
				SYN_MEM[SYN_PTR:SYN_PTR+len(code)] = code
				SYN_PTR += len(code)
	except Exception as ex:
		raise Exception('Error at line {}'.format(line_no)) from ex

# Second pass
SYN_MEM = [0] * 32768
SYN_PTR = 0

with open(args.file, 'r') as source:
	try:
		while True:
			instructions, inst_labels = assemble_next_instruction(source)
			if instructions is None:
				break
			for instruction in instructions:
				code = instruction.assemble(labels)
				SYN_MEM[SYN_PTR:SYN_PTR+len(code)] = code
				SYN_PTR += len(code)
	except Exception as ex:
		raise Exception('Error at line {}'.format(line_no)) from ex

with open(args.output, 'wb') as f:
	f.write(struct.pack('<32768H', *SYN_MEM))
