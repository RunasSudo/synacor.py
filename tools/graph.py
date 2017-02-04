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
import textwrap

rooms = {}

class Door:
	def __init__(self):
		self.name = None
		self.destination = None

class Room:
	def __init__(self):
		self.location = None
		self.name = None
		self.description = None
		self.doors = []
		self.callback = None
	
	def __str__(self):
		return """<
{:04x}: {}
<br/>{}
{}
>""".format(
			self.location,
			self.name,
			'<br/>'.join(textwrap.wrap(textwrap.shorten(self.description, 300), 50)),
			'<br/><font point-size="10">Callback: {:04x}</font>'.format(self.callback) if self.callback != 0 else '')

items = {}

class Item:
	def __init__(self):
		self.location = None
		self.name = None
		self.description = None
		self.room = None
		self.callback = None
	
	
	def __str__(self):
		return """<
{:04x}: {}
<br/>{}
{}
>""".format(
			self.location,
			self.name,
			'<br/>'.join(textwrap.wrap(textwrap.shorten(self.description, 300), 50)),
			'<br/><font point-size="10">Callback: {:04x}</font>'.format(self.callback) if self.callback != 0 else '')

# Read code into memory
SYN_MEM = [0] * 32768

with open('../dumps/init.raw', 'rb') as data:
	i = 0
	while True:
		byteData = data.read(2)
		if len(byteData) < 2:
			break
		SYN_MEM[i] = struct.unpack('<H', byteData)[0]
		i += 1

def traverse_room(location):
	if location in rooms:
		return
	
	# Read data from initial struct
	ptr_name = SYN_MEM[location]
	ptr_description = SYN_MEM[location + 1]
	ptr_door_names = SYN_MEM[location + 2]
	ptr_door_dests = SYN_MEM[location + 3]
	ptr_callback = SYN_MEM[location + 4]
	
	room = Room()
	room.location = location
	rooms[location] = room
	
	# Name
	len_name = SYN_MEM[ptr_name]
	room.name = bytes(SYN_MEM[ptr_name+1:ptr_name+1+len_name]).decode('ascii')
	
	# Description
	if ptr_description == 0x6952:
		# o_O
		ptr_description = 0x1f4f
	
	len_description = SYN_MEM[ptr_description]
	room.description = bytes(SYN_MEM[ptr_description+1:ptr_description+1+len_description]).decode('ascii')
	
	# Callback
	room.callback = ptr_callback
	
	# Door names
	door_name_ptrs = []
	len_door_name_ptrs = SYN_MEM[ptr_door_names]
	door_name_ptrs = SYN_MEM[ptr_door_names+1:ptr_door_names+1+len_door_name_ptrs]
	
	# Door dests
	door_dests = []
	len_door_dest_ptrs = SYN_MEM[ptr_door_dests]
	door_dest_ptrs = SYN_MEM[ptr_door_dests+1:ptr_door_dests+1+len_door_dest_ptrs]
	
	assert len(door_name_ptrs) == len(door_dest_ptrs)
	
	# Process doors
	for i in range(len(door_name_ptrs)):
		door = Door()
		
		len_door_name = SYN_MEM[door_name_ptrs[i]]
		door.name = bytes(SYN_MEM[door_name_ptrs[i]+1:door_name_ptrs[i]+1+len_door_name]).decode('ascii')
		
		door.destination = door_dest_ptrs[i]
		
		room.doors.append(door)
	
	for door in room.doors:
		traverse_room(door.destination)

def traverse_item(location):
	if location in items:
		return
	
	# Read data from initial struct
	ptr_name = SYN_MEM[location]
	ptr_description = SYN_MEM[location + 1]
	ptr_room = SYN_MEM[location + 2]
	ptr_callback = SYN_MEM[location + 3]
	
	item = Item()
	item.location = location
	items[location] = item
	
	# Name
	len_name = SYN_MEM[ptr_name]
	item.name = bytes(SYN_MEM[ptr_name+1:ptr_name+1+len_name]).decode('ascii')
	
	# Description
	len_description = SYN_MEM[ptr_description]
	item.description = bytes(SYN_MEM[ptr_description+1:ptr_description+1+len_description]).decode('ascii')
	
	# Callback
	item.callback = ptr_callback
	
	# Room
	if ptr_room != 0x7fff:
		item.room = ptr_room
		if ptr_room not in rooms:
			traverse_room(ptr_room)

# Seed rooms
traverse_room(0x090d) # Foothills
traverse_room(0x09b8) # Synacor Headquarters
traverse_room(0x09cc) # Beachside

# Exhaustive check
for i in range(0x090d, 0x099e, 5):
	if i not in rooms:
		traverse_room(i)
for i in range(0x099f, 0x0a6c, 5):
	if i not in rooms:
		traverse_room(i)
for i in range(0x0a6c, 0x0aac, 4):
	if i not in items:
		traverse_item(i)

import graphviz

dot = graphviz.Digraph()

for code, room in rooms.items():
	dot.node('{:04x}'.format(code), str(room))
	for door in room.doors:
		dot.edge('{:04x}'.format(code), '{:04x}'.format(door.destination), door.name)

for code, item in items.items():
	dot.node('{:04x}'.format(code), str(item), style='dashed')
	if item.room is not None:
		dot.edge('{:04x}'.format(item.room), '{:04x}'.format(code), style='dashed')

print(dot.source)
