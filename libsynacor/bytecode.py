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

class Operand:
	@staticmethod
	def read_op(word):
		if 0 <= word <= 32767:
			return OpLiteral(word)
		if 32768 <= word <= 32775:
			return OpRegister(word - 32768)
		raise Exception('Invalid word {}')

class OpLiteral(Operand):
	def __init__(self, value):
		self.value = value
	def get(self, cpu):
		return self.value
	def set(self, cpu, value):
		raise Exception('Attempted to set literal value {} to {} at {}'.format(self.value, value, cpu.SYN_PTR))

class OpRegister(Operand):
	def __init__(self, register):
		self.register = register
	def get(self, cpu):
		return cpu.SYN_REG[self.register]
	def set(self, cpu, value):
		cpu.SYN_REG[self.register] = value

instructions_by_opcode = {}
instructions_by_name = {}

def instruction(opcode, name, nargs=0):
	def decorator(cls):
		cls.opcode = opcode
		cls.name = name
		cls.nargs = nargs
		
		instructions_by_opcode[opcode] = cls
		instructions_by_name[name] = cls
		
		return cls
	return decorator

class Instruction:
	def __init__(self):
		self.args = []
	
	@staticmethod
	def next_instruction(data, idx):
		opcode = Operand.read_op(data[idx])
		idx += 1
		
		if not isinstance(opcode, OpLiteral):
			raise Exception('Invalid value for opcode {} at {}'.format(data[idx], idx))
		opcode_value = opcode.get(None)
		if opcode_value not in instructions_by_opcode:
			raise Exception('Invalid opcode {} at {}'.format(opcode_value, idx))
		
		instruction = instructions_by_opcode[opcode_value]()
		for _ in range(instruction.nargs):
			instruction.args.append(Operand.read_op(data[idx]))
			idx += 1
		
		return instruction, idx

@instruction(21, 'nop')
class InstructionNop(Instruction):
	def run(self, cpu):
		pass

@instruction(0, 'halt')
class InstructionHalt(Instruction):
	def run(self, cpu):
		import sys
		sys.exit(0)

@instruction(1, 'set', 2)
class InstructionSet(Instruction):
	def run(self, cpu):
		self.args[0].set(cpu, self.args[1].get(cpu))

@instruction(2, 'push', 1)
class InstructionPush(Instruction):
	def run(self, cpu):
		cpu.SYN_STK.append(self.args[0].get(cpu))

@instruction(3, 'pop', 1)
class InstructionPop(Instruction):
	def run(self, cpu):
		if len(cpu.SYN_STK) == 0:
			raise Exception('Attempted to pop from empty stack at {}'.format(cpu.SYN_PTR))
		self.args[0].set(cpu, cpu.SYN_STK.pop())

@instruction(4, 'eq', 3)
class InstructionEq(Instruction):
	def run(self, cpu):
		self.args[0].set(cpu, 1 if self.args[1].get(cpu) == self.args[2].get(cpu) else 0)

@instruction(5, 'gt', 3)
class InstructionGt(Instruction):
	def run(self, cpu):
		self.args[0].set(cpu, 1 if self.args[1].get(cpu) > self.args[2].get(cpu) else 0)

@instruction(6, 'jmp', 1)
class InstructionJmp(Instruction):
	def run(self, cpu):
		cpu.SYN_PTR = self.args[0].get(cpu)

@instruction(7, 'jt', 2)
class InstructionJt(Instruction):
	def run(self, cpu):
		if self.args[0].get(cpu) != 0:
			cpu.SYN_PTR = self.args[1].get(cpu)

@instruction(8, 'jf', 2)
class InstructionJf(Instruction):
	def run(self, cpu):
		if self.args[0].get(cpu) == 0:
			cpu.SYN_PTR = self.args[1].get(cpu)

@instruction(9, 'add', 3)
class InstructionAdd(Instruction):
	def run(self, cpu):
		self.args[0].set(cpu, (self.args[1].get(cpu) + self.args[2].get(cpu)) % 32768)

@instruction(10, 'mult', 3)
class InstructionMult(Instruction):
	def run(self, cpu):
		self.args[0].set(cpu, (self.args[1].get(cpu) * self.args[2].get(cpu)) % 32768)

@instruction(11, 'mod', 3)
class InstructionMod(Instruction):
	def run(self, cpu):
		self.args[0].set(cpu, self.args[1].get(cpu) % self.args[2].get(cpu))

@instruction(12, 'and', 3)
class InstructionAnd(Instruction):
	def run(self, cpu):
		self.args[0].set(cpu, self.args[1].get(cpu) & self.args[2].get(cpu))

@instruction(13, 'or', 3)
class InstructionOr(Instruction):
	def run(self, cpu):
		self.args[0].set(cpu, self.args[1].get(cpu) | self.args[2].get(cpu))

@instruction(14, 'not', 2)
class InstructionNot(Instruction):
	def run(self, cpu):
		self.args[0].set(cpu, ~self.args[1].get(cpu) % 32768)

@instruction(15, 'rmem', 2)
class InstructionRmem(Instruction):
	def run(self, cpu):
		self.args[0].set(cpu, cpu.SYN_MEM[self.args[1].get(cpu)])

@instruction(16, 'wmem', 2)
class InstructionWmem(Instruction):
	def run(self, cpu):
		cpu.SYN_MEM[self.args[0].get(cpu)] = self.args[1].get(cpu)

@instruction(17, 'call', 1)
class InstructionCall(Instruction):
	def run(self, cpu):
		cpu.SYN_STK.append(cpu.SYN_PTR)
		cpu.SYN_PTR = self.args[0].get(cpu)

@instruction(18, 'ret')
class InstructionRet(Instruction):
	def run(self, cpu):
		if len(cpu.SYN_STK) == 0:
			raise Exception('Attempted to return with empty stack at {}'.format(cpu.SYN_PTR))
		cpu.SYN_PTR = cpu.SYN_STK.pop()

@instruction(19, 'out', 1)
class InstructionOut(Instruction):
	def run(self, cpu):
		print(chr(self.args[0].get(cpu)), end='')

@instruction(20, 'in', 1)
class InstructionIn(Instruction):
	def run(self, cpu):
		import sys
		
		while len(cpu.SYN_STDIN_BUF) == 0:
			line = sys.stdin.readline()
			if line.startswith('.'):
				# Debug command
				dbg_args = line[1:].split()
				with open(dbg_args[0] + '.py', 'r') as f:
					exec(f.read(), globals(), locals())
			else:
				cpu.SYN_STDIN_BUF = list(line)
		
		self.args[0].set(cpu, ord(cpu.SYN_STDIN_BUF.pop(0)))
