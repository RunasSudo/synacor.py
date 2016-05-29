#!/usr/bin/env python3
#    synacor.py - An implementation of the Synacor Challenge
#    Copyright © 2016  RunasSudo
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

import struct # for bytes<-->word handling
import sys # for stdin

SYN_PTR = 0
SYN_MEM = [0] * 32768
SYN_REG = [0] * 8
SYN_STK = []

class OpLiteral:
	def __init__(self, value):
		self.value = value;
	def get(self):
		return self.value;
	def set(self, value):
		raise Exception('Attempted to set literal value {} to {} at {}'.format(self.value, value, SYN_PTR))

class OpRegister:
	def __init__(self, register):
		self.register = register;
	def get(self):
		return SYN_REG[self.register];
	def set(self, value):
		SYN_REG[self.register] = value;

def readOp(word):
	if 0 <= word <= 32767:
		return OpLiteral(word)
	if 32768 <= word <= 32775:
		return OpRegister(word - 32768)
	raise Exception('Invalid word {} at {}'.format(word, SYN_PTR))

def swallowOp():
	global SYN_PTR
	op = readOp(SYN_MEM[SYN_PTR])
	SYN_PTR += 1
	return op

# Read code into memory
with open('challenge.bin', 'rb') as data:
	while True:
		byteData = data.read(2)
		if len(byteData) < 2:
			break
		SYN_MEM[SYN_PTR] = struct.unpack('<H', byteData)[0]
		SYN_PTR += 1

SYN_PTR = 0

# Begin execution
while True:
	instruction = swallowOp().get()
	
	if instruction == 21: #NOP
		pass
	elif instruction == 0: #HALT
		sys.exit(0)
	elif instruction == 1: #SET
		swallowOp().set(swallowOp().get())
	elif instruction == 2: #PUSH
		SYN_STK.append(swallowOp().get())
	elif instruction == 3: #POP
		if len(SYN_STK) == 0:
			raise Exception('Attempted to pop from empty stack at {}'.format(SYN_PTR))
		swallowOp().set(SYN_STK.pop())
	elif instruction == 4: #EQ
		swallowOp().set(1 if swallowOp().get() == swallowOp().get() else 0)
	elif instruction == 5: #GT
		swallowOp().set(1 if swallowOp().get() > swallowOp().get() else 0)
	elif instruction == 6: #JMP
		SYN_PTR = swallowOp().get()
	elif instruction == 7: #JT (jump if not zero)
		a, b = swallowOp().get(), swallowOp().get()
		if a != 0:
			SYN_PTR = b
	elif instruction == 8: #JF (jump if zero)
		a, b = swallowOp().get(), swallowOp().get()
		if a == 0:
			SYN_PTR = b
	elif instruction == 9: #ADD
		swallowOp().set((swallowOp().get() + swallowOp().get()) % 32768)
	elif instruction == 10: #MULT
		swallowOp().set((swallowOp().get() * swallowOp().get()) % 32768)
	elif instruction == 11: #MOD
		swallowOp().set(swallowOp().get() % swallowOp().get())
	elif instruction == 12: #AND
		swallowOp().set(swallowOp().get() & swallowOp().get())
	elif instruction == 13: #OR
		swallowOp().set(swallowOp().get() | swallowOp().get())
	elif instruction == 14: #NOT
		swallowOp().set(~swallowOp().get() % 32768) # mathemagic
	elif instruction == 15: #RMEM
		swallowOp().set(SYN_MEM[swallowOp().get()])
	elif instruction == 16: #WMEM
		a, b = swallowOp().get(), swallowOp().get()
		SYN_MEM[a] = b # order of operations
	elif instruction == 17: #CALL
		SYN_STK.append(SYN_PTR + 1) # skip one word for the operand
		SYN_PTR = swallowOp().get()
	elif instruction == 18: #RET
		if len(SYN_STK) == 0:
			raise Exception('Attempted to return with empty stack at {}'.format(SYN_PTR))
		SYN_PTR = SYN_STK.pop()
	elif instruction == 19: #OUT
		print(chr(swallowOp().get()), end='')
	elif instruction == 20: #IN
		swallowOp().set(ord(sys.stdin.read(1))) # the spec says a whole line will be read, so ¯\_(ツ)_/¯
	else:
		raise Exception('Unimplemented opcode {} at {}'.format(instruction, SYN_PTR))
