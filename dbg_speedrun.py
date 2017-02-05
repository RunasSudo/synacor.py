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

import io
import sys

transcript = """take tablet
use tablet
doorway
north
north
bridge
continue
down
east
take empty lantern
west
west
passage
ladder
west
south
north
take can
use can
use lantern
west
ladder
darkness
continue
west
west
west
west
north
take red coin
north
west
take blue coin
up
take shiny coin
down
east
east
take concave coin
down
take corroded coin
up
west
use blue coin
use red coin
use shiny coin
use concave coin
use corroded coin
north
take teleporter
use teleporter
.dbg_teleporter
use teleporter
north
north
north
north
north
north
north
north
north
take orb
north
east
east
north
west
south
east
east
west
north
north
east
vault
take mirror
use mirror
"""

# Read code into memory
SYN_PTR = 0
with open('challenge.bin', 'rb') as data:
	while True:
		byteData = data.read(2)
		if len(byteData) < 2:
			break
		SYN_MEM[SYN_PTR] = struct.unpack('<H', byteData)[0]
		SYN_PTR += 1
SYN_PTR = 0

# We cannot directly set SYN_STDIN_BUF since debug commands are processed only at stdin read
sys.stdin = io.StringIO(transcript)
