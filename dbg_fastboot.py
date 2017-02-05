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

import pickle

# Read code into memory
SYN_MEM = [0] * 32768

with open('challenge.bin', 'rb') as data:
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

# Jump past self-test
SYN_PTR = 0x0377
