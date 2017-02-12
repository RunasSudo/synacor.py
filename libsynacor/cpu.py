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

class CPU:
	def __init__(self):
		self.SYN_PTR = 0
		self.SYN_MEM = [0] * 32768
		self.SYN_REG = [0] * 8
		self.SYN_STK = []
		self.SYN_STDIN_BUF = []
	
	def swallow_op(self):
		op = Operand.read_op(self.SYN_MEM[self.SYN_PTR])
		self.SYN_PTR += 1
	
	def step(self):
		instruction, self.SYN_PTR = Instruction.next_instruction(self.SYN_MEM, self.SYN_PTR)
		instruction.run(self)
