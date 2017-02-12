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

# Emulate 06bb
for R1 in range(0x17b4, 0x7562):
	R0 = cpu.SYN_MEM[R1]
	R0 ^= pow(R1, 2, 32768)
	R0 ^= 0x4154
	cpu.SYN_MEM[R1] = R0

# Jump past self-test
cpu.SYN_PTR = 0x0377
