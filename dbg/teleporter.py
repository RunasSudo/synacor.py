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

# Set R7 to 6486
cpu.SYN_REG[7] = 0x6486

# Patch instructions 1571 to 1579 inclusive with nop's
cpu.SYN_MEM[0x1571:0x157a] = [21] * 9

print('Patched. Ready to run "use teleporter".')
