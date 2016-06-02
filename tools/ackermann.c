/*
    synacor.py - An implementation of the Synacor Challenge
    Copyright © 2016  RunasSudo

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define NUM_THREADS 8

static uint16_t A(uint16_t R1, uint16_t R2, uint16_t R8, uint16_t cache[5][0x8000]) {
	if (cache[R1][R2] != 0xffff) {
		return cache[R1][R2];
	}
	
	if (R1 == 0)
		return (R2 + 1) & 0x7fff;
	if (R2 == 0)
		return A(R1 - 1, R8, R8, cache);
	
	return A(R1 - 1, cache[R1][R2 - 1] = A(R1, R2 - 1, R8, cache), R8, cache);
}

static void* bruteThread(void* rmdrVoid) {
	uint16_t rmdr;
	uint16_t cache[5][0x8000];
	uint16_t R8;
	
	rmdr = *((int *) rmdrVoid);
	
	for (R8 = rmdr; R8 <= 0x7fff; R8 += NUM_THREADS) {
		memset(cache, 0xff, sizeof(cache)); /* Clear the cache */
		
		if (!(R8 & 0xff))
			printf("%04x...\n", R8);
		
		if (A(4, 1, R8, cache) == 6)
			printf("Found a solution! %04x...\n", R8);
	}
}

int main() {
	pthread_t threads[NUM_THREADS];
	int thread_args[NUM_THREADS];
	int i;
	
	for (i = 0; i < NUM_THREADS; i++) {
		printf("Spawning thread %d...\n", i);
		thread_args[i] = i; /* rmdr */
		pthread_create(&threads[i], NULL, bruteThread, (void*) &thread_args[i]);
	}
	
	/* wait */
	for (i = 0; i < NUM_THREADS; i++) {
		pthread_join(threads[i], NULL);
	}
	
	printf("Search complete\n");
}
