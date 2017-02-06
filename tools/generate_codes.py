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

import struct
import sys

IV_LEN = 3
CODE_LEN = 12

# Emulate 0731
def generate_code(R1, R2, R3, R4):
	R2data = SYN_MEM[R2+1:R2+1+SYN_MEM[R2]]
	R4data = SYN_MEM[R4+1:R4+1+SYN_MEM[R4]]
	
	assert len(R4data) == IV_LEN
	
	done = False
	while not done:
		code = ''
		for i in range(CODE_LEN):
			R6 = i % IV_LEN
			R7 = R4data[R6]
			R7 = (R7 * 0x1481) % 0x8000
			R7 = (R7 + 0x3039) % 0x8000
			R4data[R6] = R7
			R7 = R1 ^ R7
			R7 = R7 % len(R2data)
			if R7 + 1 <= R3:
				done = True
			R7 = R2data[R7]
			code += chr(R7)
	return code

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
for R2 in range(0x17b4, 0x7562):
	R1 = SYN_MEM[R2]
	R1 ^= pow(R2, 2, 32768)
	R1 ^= 0x4154
	SYN_MEM[R2] = R1

# Calls to 0731
CODE_PARAMS = [
	(0x0058, 0x650a, 0x7fff, 0x6e8b), # R1 from the maze
	(0x1092, 0x650a, 0x7fff, 0x6eed),
	(0x6486, 0x650a, 0x7fff, 0x7239), # R1 is R8 from Ackermann
	(0x0b3b, 0x650a, 0x7fff, 0x73df), # R1 from the dots on the coins
	# 1691 is a bit tricky
]

for cp in CODE_PARAMS:
	print(generate_code(*cp))
