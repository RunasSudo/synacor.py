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

import struct # for bytes<-->word handling
import sys # for args

# Read code into memory
SYN_MEM = [0] * 32768

with open(sys.argv[1], 'rb') as data:
	i = 0
	while True:
		byteData = data.read(2)
		if len(byteData) < 2:
			break
		SYN_MEM[i] = struct.unpack('<H', byteData)[0]
		i += 1

# Emulate 06bb
for R1 in range(0x17b4, 0x7562):
	R0 = SYN_MEM[R1]
	R0 ^= pow(R1, 2, 32768)
	R0 ^= 0x4154
	SYN_MEM[R1] = R0

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
	global SYN_PTR
	word = SYN_MEM[SYN_PTR]
	SYN_PTR += 1
	return word

def readOp():
	word = readWord()
	if 0 <= word <= 32767:
		return OpLiteral(word)
	if 32768 <= word <= 32775:
		return OpRegister(word - 32768)
	raise Exception('Invalid word {} at {}'.format(word, SYN_PTR))

def escapeChar(char):
	return char.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')

SYN_PTR = 0

while SYN_PTR < len(SYN_MEM):
	word = readWord()
	
	if word == 21: #NOP
		pass
	elif word == 0: #HALT
		pass
	elif word == 1: #SET
		readOp()
		readOp()
	elif word == 2: #PUSH
		readOp()
	elif word == 3: #POP
		readOp()
	elif word == 4: #EQ
		readOp()
		readOp()
		readOp()
	elif word == 5: #GT
		readOp()
		readOp()
		readOp()
	elif word == 6: #JMP
		readOp()
	elif word == 7: #JT (jump if not zero)
		readOp()
		readOp()
	elif word == 8: #JF (jump if zero)
		readOp()
		readOp()
	elif word == 9: #ADD
		readOp()
		readOp()
		readOp()
	elif word == 10: #MULT
		readOp()
		readOp()
		readOp()
	elif word == 11: #MOD
		readOp()
		readOp()
		readOp()
	elif word == 12: #AND
		readOp()
		readOp()
		readOp()
	elif word == 13: #OR
		readOp()
		readOp()
		readOp()
	elif word == 14: #NOT
		readOp()
		readOp()
	elif word == 15: #RMEM
		readOp()
		readOp()
	elif word == 16: #WMEM
		readOp()
		readOp()
	elif word == 17: #CALL
		if readWord() == 0x05b2:
			if (SYN_MEM[SYN_PTR-9:SYN_PTR-6] == [1, 32769, 0x05fb] # set R1 05fb
			and SYN_MEM[SYN_PTR-12:SYN_PTR-10] == [1, 32768] # set R0 XXXX
			and SYN_MEM[SYN_PTR-6:SYN_PTR-4] == [9, 32770]): # add R2 XXXX XXXX
				# Got an encrypted string!
				R0 = SYN_MEM[SYN_PTR-10]
				R2 = (SYN_MEM[SYN_PTR-4] + SYN_MEM[SYN_PTR-3]) % 32768
				#print('{:04x} {:04x}'.format(R0, R2))
				
				strlen = SYN_MEM[R0]
				strbuf = ''
				for i in range(strlen):
					encrypted = SYN_MEM[R0 + 1 + i]
					decrypted = encrypted ^ R2
					strbuf += escapeChar(chr(decrypted))
				
				print('{:04x}: "{}"'.format(R0, strbuf))
	elif word == 18: #RET
		pass
	elif word == 19: #OUT
		readOp()
	elif word == 20: #IN
		readOp()
	else: #data
		pass
