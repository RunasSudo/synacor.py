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

def memory_from_file(data):
	import struct
	SYN_MEM = [0] * 32768
	SYN_PTR = 0
	while True:
		byteData = data.read(2)
		if len(byteData) < 2:
			break
		SYN_MEM[SYN_PTR] = struct.unpack('<H', byteData)[0]
		SYN_PTR += 1
	return SYN_MEM
