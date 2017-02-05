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

import collections
import re
import struct
import sys

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
		
		self.is_operator = False
		self.mutate_value = None

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
	
	# Name
	len_name = SYN_MEM[ptr_name]
	room.name = bytes(SYN_MEM[ptr_name+1:ptr_name+1+len_name]).decode('ascii')
	
	if room.name.startswith('Vault '):
		rooms[location] = room
	else:
		return
	
	# Description
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
	
	# Parse description
	if room.name == 'Vault Antechamber':
		room.mutate_value = lambda val: '22'
	else:
		match = re.search(r"mosaic depicting the number '(.*)'", room.description)
		if match:
			room_value = match.group(1)
			room.mutate_value = lambda val: val + room_value + ')'
		else:
			match = re.search(r"mosaic depicting a '(.*)' symbol", room.description)
			if match:
				room.is_operator = True
				room_operator = match.group(1)
				room.mutate_value = lambda val: '(' + val + room_operator
			else:
				raise Exception('Unable to parse description: {}'.format(room.description))
	
	for door in room.doors:
		traverse_room(door.destination)

# Seed rooms
traverse_room(0x0a3f)

# Breadth-first search

queue = collections.deque()
initial_status = ([(None, 0x0a3f)], None) # current path, previous value
queue.append(initial_status)

while True:
	current_status = queue.popleft()
	current_room = current_status[0][-1][1]
	current_value = rooms[current_room].mutate_value(current_status[1])
	
	print(current_status)
	print(current_value)
	
	if current_room == 0x0a12: # Vault Door
		if eval(current_value) == 30:
			# We have reached the goal
			sys.exit(0)
		else:
			# We must not enter the vault door unless we have the right number, else the orb will disappear
			# Do not continue this line of searching
			continue
	
	for edge in rooms[current_room].doors:
		if edge.destination in rooms:
			new_status = (current_status[0] + [(edge.name, edge.destination)], current_value)
			queue.append(new_status)
