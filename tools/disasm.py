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
import sys # for args

class OpLiteral:
	def __init__(self, value):
		self.value = value;
	def get(self):
		return '{:04x}'.format(self.value);
	def set(self):
		return '{:04x}'.format(self.value);

class OpRegister:
	def __init__(self, register):
		self.register = register;
	def get(self):
		return 'R{}'.format(self.register + 1);
	def set(self):
		return 'R{}'.format(self.register + 1);

def readWord():
	byteData = data.read(2)
	if len(byteData) < 2:
		return None
	return struct.unpack('<H', byteData)[0]

def readOp():
	word = readWord()
	if 0 <= word <= 32767:
		return OpLiteral(word)
	if 32768 <= word <= 32775:
		return OpRegister(word - 32768)
	raise Exception('Invalid word {} at {}'.format(word, SYN_PTR))

def escapeChar(char):
	return char.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')

MODE_OUT = False
MODE_DAT = False #False, 1 (data), 2 (text)

with open(sys.argv[1], 'rb') as data:
	while True:
		pos = int(data.tell() / 2)
		
		word = readWord()
		if word == None:
			break
		
		if MODE_OUT and word != 19:
			print('"')
			MODE_OUT = False
		if MODE_DAT and 0 <= word <= 21:
			if MODE_DAT == 1:
				print()
			if MODE_DAT == 2:
				print('"')
			MODE_DAT = False
		
		if word == 21: #NOP
			print('{:04x} nop'.format(pos))
		elif word == 0: #HALT
			print('{:04x} halt'.format(pos))
		elif word == 1: #SET
			print('{:04x} set  {} {}'.format(pos, readOp().set(), readOp().get()))
		elif word == 2: #PUSH
			print('{:04x} push {}'.format(pos, readOp().get()))
		elif word == 3: #POP
			print('{:04x} pop  {}'.format(pos, readOp().set()))
		elif word == 4: #EQ
			print('{:04x} eq   {} {} {}'.format(pos, readOp().set(), readOp().get(), readOp().get()))
		elif word == 5: #GT
			print('{:04x} gt   {} {} {}'.format(pos, readOp().set(), readOp().get(), readOp().get()))
		elif word == 6: #JMP
			print('{:04x} jmp  {}'.format(pos, readOp().get()))
		elif word == 7: #JT (jump if not zero)
			print('{:04x} jt   {} {}'.format(pos, readOp().get(), readOp().get()))
		elif word == 8: #JF (jump if zero)
			print('{:04x} jf   {} {}'.format(pos, readOp().get(), readOp().get()))
		elif word == 9: #ADD
			print('{:04x} add  {} {} {}'.format(pos, readOp().set(), readOp().get(), readOp().get()))
		elif word == 10: #MULT
			print('{:04x} mult {} {} {}'.format(pos, readOp().set(), readOp().get(), readOp().get()))
		elif word == 11: #MOD
			print('{:04x} mod  {} {} {}'.format(pos, readOp().set(), readOp().get(), readOp().get()))
		elif word == 12: #AND
			print('{:04x} and  {} {} {}'.format(pos, readOp().set(), readOp().get(), readOp().get()))
		elif word == 13: #OR
			print('{:04x} or   {} {} {}'.format(pos, readOp().set(), readOp().get(), readOp().get()))
		elif word == 14: #NOT
			print('{:04x} not  {} {}'.format(pos, readOp().set(), readOp().get()))
		elif word == 15: #RMEM
			print('{:04x} rmem {} {}'.format(pos, readOp().set(), readOp().get()))
		elif word == 16: #WMEM
			print('{:04x} wmem {} {}'.format(pos, readOp().set(), readOp().get()))
		elif word == 17: #CALL
			print('{:04x} call {}'.format(pos, readOp().get()))
		elif word == 18: #RET
			print('{:04x} ret'.format(pos))
		elif word == 19: #OUT
			op = readOp()
			
			if isinstance(op, OpLiteral):
				if MODE_OUT:
					print(escapeChar(chr(op.value)), end='')
				else:
					print('{:04x} out  "{}'.format(pos, escapeChar(chr(op.value))), end='')
					MODE_OUT = True
				if op.value == 0x0a:
					print('"')
					MODE_OUT = False # break on newlines
			else:
				if MODE_OUT:
					print('"')
					MODE_OUT = False
				print('{:04x} out  {}'.format(pos, op.get(), end=''))
		elif word == 20: #IN
			print('{:04x} in   {}'.format(pos, readOp().set()))
		else:
			if 32 <= word <= 126:
				# looks like letters - unfortunately "\n" looks like MULT
				if MODE_DAT == 2:
					print(escapeChar(chr(word)), end='')
				else:
					if MODE_DAT == 1:
						print()
					print('{:04x} data "{}'.format(pos, escapeChar(chr(word))), end='')
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
					print('{:04x} data {:04x}'.format(pos, word), end='')
					MODE_DAT = 1
