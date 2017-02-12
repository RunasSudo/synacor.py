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

import sys

cpu = CPU()
with open(sys.argv[1], 'rb') as data:
	cpu.SYN_MEM = memory_from_file(data)

if len(sys.argv) > 2:
	dbg_args = sys.argv[2:]
	with open(dbg_args[0] + '.py', 'r') as f:
		exec(f.read(), globals(), locals())

while True:
	cpu.step()
