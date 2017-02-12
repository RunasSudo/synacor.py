#    synacor.py - An implementation of the Synacor Challenge
#    Copyright © 2016–2017  RunasSudo
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

if len(dbg_args) < 2:
	print('Usage: {} {} <file>'.format(sys.argv[0], dbg_args[0]))
else:
	with open(dbg_args[1], 'rb') as f:
		model = pickle.load(f)
	
	cpu.SYN_PTR = model['SYN_PTR']
	cpu.SYN_MEM = model['SYN_MEM']
	cpu.SYN_REG = model['SYN_REG']
	cpu.SYN_STK = model['SYN_STK']
