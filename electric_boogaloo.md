# Synacor Challenge 2: Electric Boogaloo

So we've finished the official parts of the challenge. What now?

## Self-test

Hex values refer to the instruction lines, not the actual ranges spanned by the data in memory

* `0000` to `013e`: Startup message
* `0140` to `01e3`: Tests `jmp`
  * From `0160` to `01c9`, some clever code is used to ‘amplify’ the effect of any error in `jmp` to allow the precise size of the error to be determined.
  * If successful, executes `0140`, `015b` to `0160`, then `0166`.
* `01e4` to `01f2`: Tests `jt` and `jf`
  * If successful, jumps to `01f4`.
* `01f4` to `0209`: Tests that the registers are initialised to zero
* `020c` to `0215`: Tests `set`
* `0218` to `0233`: Tests `add`
  * The test is rudimentary, however, and would not detect many simple errors. In fact it tests only if 1 + 1 ≠ 0.
* `0234` to `024d`: Tests `eq`
  * Surprisingly, this is where it is checked that 1 + 1 = 2, but if `add` gives an incorrect non-zero result for 1 + 1, the test will erroneously report that it is `eq` which is not supported!
  * It would probably have been a better idea to test `eq` first, before `add`, then use `eq` to test `add`.
* `024e` to `0261`: Tests `push` and `pop`
  * Since only `R0` and `R1` are checked, this would not detect errors involving other registers.
  * This test, like the last one, reuses the results of previous tests, since that worked out so well for `eq`…
* `0264` to `0276`: Tests `gt`
  * The tests performed seem quite reasonable, but yet again reuse the results of previous tests…
* `0279` to `02ab`: Tests `and` and `or`
  * Confusingly, the error handling is located in different places for each test.
* `02ac` to `02bd`: Tests `not`
  * Okay, I admit this one was pretty helpful. What the hell is a ‘15-bit bitwise inverse’? Well the test passes if I do just do mod 32768, so that works I guess…
* `02c0` to `02e8`: Tests `call`
  * Although, notably, not `ret`. The tests operates by `jmp`ing back and forth to test the various values of `R0`.
* `02eb` to `0308`: Checks that `add` overflows correctly
* `030b` to `0313`: Checks that 6 × 9 ≠ 42.
  * I suspect there is a mistake in this test. Since Adams (1979) demonstrated unequivocally that 6 × 9 is equal to 42, I believe the `jt` should in fact be a `jf`.
* `0316` to `0346`: Continues checking `mult`
* `0349` to `034b`: Two values `4e20` and `2710` are stored in memory here for reference by the following test
* `034d` to `03d1`: Tests `rmem` and `wmem`
  * If successful, causes the words from `03a9` to `03ac` to instead read `nop`, `jt 0013 03d2`
  * There is more to the portion starting `0375` than meets the eye: see below.
* `0432` to `05b1`: Various error messages

## Decryption

As we know from earlier, most of the strings in the binary are encrypted (or at the very least obfuscated) in some way, and decrypted following the self-test. It is therefore desirable to study this encryption before further study of the binary.

After a wild goose chase examining the code after the self-test, we find that the decryption actually happens *during* the `rmem`/`wmem` test! Very sneaky!

    0375 call 06bb

This is the magic line. Digging into the `06bb` subroutine:

    06bb push R0
    06bd push R1
    06bf set  R1 17b4
    06c2 rmem R0 R1
    06c5 push R1
    06c7 mult R1 R1 R1
    06cb call 084d
    06cd set  R1 4154
    06d0 call 084d
    06d2 pop  R1
    06d4 wmem R1 R0
    06d7 add  R1 R1 0001
    06db eq   R0 7562 R1
    06df jf   R0 06c2
    06e2 pop  R1
    06e4 pop  R0
    06e6 ret

Inspecting the `084d` subroutine reveals that this is simply an XOR function: `R0 XOR R1`. Crypto rating: 1/10

Rewriting `06bb` function using higher-level syntax reveals that the ‘encryption’ algorithm is really very simple:

```c
06bb() {
	R1 = 17b4;
	for (R1 = 17b4; R1 != 7562; R1++) {
		R0 = [R1];
		R0 ^= R1 * R1;
		R0 ^= 4154;
		[R1] = R0;
	}
}
```

*Very* simple.

[By emulating this function in Python](https://github.com/RunasSudo/synacor.py/blob/master/dbg_fastboot.py), we can skip the self-test and computationally-expensive decryption process entirely, and get straight into the good stuff next time we want to play!

## Encrypted strings

So earlier, we produced a tool-assisted speed-run that would complete and dump the codes for any given challenge binary, but where's the fun in that? Why not extract the codes from the binary directly? Of course, this is easier said than done. None of the codes, nor any of the strings relating to them, are visible in the disassembled binary, whether before or after the decryption from the previous section.

Looking through the code following the self-test, we find:

    0413 set  R0 17c0
    0416 call 05ee

Digging deeper, `05ee` calls `05b2` with `R1` set to `05f8`. `05b2` appears to iterate over the characters in a string whose length is stored in address `R0`, and calls `R1` for each character, storing the character in `R0`. `05f8` (the callback provided by `05ee`) simply outputs every character in `R0` it gets.

Immediately after this call to `05ee`, we find:

    041e set  R0 68e3
    0421 set  R1 05fb
    0424 add  R2 XXXX XXXX
    0428 call 05b2

In other words, a similar string-handling subroutine is called, but instead of `05f8` (which would simply print the string), `05fb` is called. `05fb` also outputs the character, but only after calling `084d` (XOR) with `R1` set to `R2`.

Now we have everything we need to [extract these encrypted (double-encrypted??) strings](https://github.com/RunasSudo/synacor.py/blob/master/tools/decrypt_strings.py) from the binary!

Only the self-test completion code appears to be stored there, though, so I'm not sure what the point of encrypting those was…

## The codes

We may not have the codes themselves, but we can now easily locate where they are printed. The tablet code, for example, is conveniently sandwiched between strings `6ed1` and `6ef1`. Thus the code we are looking for is:

    1290 set  R0 1092
    1293 set  R1 650a
    1296 set  R2 7fff
    1299 set  R3 6eed
    129c call 0731

Looking into `0731`:

    0731 push R3
    0733 push R4
    0735 push R5
    0737 push R6
    0739 set  R6 0001
    073c add  R4 R3 R6
    0740 rmem R4 R4
    0743 add  R5 17ed R6
    0747 wmem R5 R4
    074a add  R6 R6 0001
    074e rmem R5 17ed
    0751 gt   R4 R6 R5
    0755 jf   R4 073c
    0758 set  R3 0000
    075b set  R4 0000
    075e rmem R5 17ed
    0761 mod  R5 R4 R5
    0765 add  R5 R5 17ed
    0769 add  R5 R5 0001
    076d rmem R6 R5
    0770 mult R6 R6 1481
    0774 add  R6 R6 3039
    0778 wmem R5 R6
    077b push R0
    077d push R1
    077f set  R1 R6
    0782 call 084d
    0784 set  R6 R0
    0787 pop  R1
    0789 pop  R0
    078b rmem R5 R1
    078e mod  R6 R6 R5
    0792 add  R6 R6 0001
    0796 gt   R5 R6 R2
    079a jt   R5 07a0
    079d set  R3 0001
    07a0 add  R6 R6 R1
    07a4 rmem R6 R6
    07a7 add  R4 R4 0001
    07ab add  R5 R4 17f1
    07af wmem R5 R6
    07b2 rmem R5 17f1
    07b5 eq   R5 R4 R5
    07b9 jf   R5 075e
    07bc jf   R3 0758
    07bf push R0
    07c1 set  R0 17f1
    07c4 call 05ee
    07c6 pop  R0
    07c8 pop  R6
    07ca pop  R5
    07cc pop  R4
    07ce pop  R3
    07d0 ret

Umm… Sorry, could you repeat that?

Rewriting this again in more friendly terms:

```c
// R0: A seed of sorts - the same for all users
// R1: The length and alphabet to use, usually 650a, but 653f for the mirror
// R2: Usually 7fff, but 0004 for the mirror
// R3: An initialisation vector of sorts - contents different for every user - points to the length, but this is always 3
0731(R0, R1, R2, R3) {
	// copy the string at R3 to 17ed
	R6 = 0001;
	do {
		R4 = R3 + R6;
		R4 = [R4];
		R5 = 17ed + R6;
		[R5] = R4;
		R6 = R6 + 0001;
		R5 = [17ed]; // 3, the length - this never seems to change
	} while (R6 <= R5);
	
	// the string at 17ed is now what was at R3
	do {
		R3 = 0000; // done flag
		R4 = 0000; // index
		do {
			R5 = [17ed]; // 3, the length
			R5 = R4 % R5;
			R5 = R5 + 17ed;
			R5 = R5 + 0001; // will cycle through three addresses of 17ed/R3 string: 17ee, 17ef, 17f0
			R6 = [R5];
			R6 = R6 * 1481;
			R6 = R6 + 3039;
			[R5] = R6; // mutate that value of the 17ed string
			R6 = R0 ^ R6; // combine R0 into R6
			R5 = [R1]; // length of the alphabet
			R6 = R6 % R5;
			R6 = R6 + 0001; // calculate index in alphabet
			if (R6 <= R2) {
				R3 = 0001; // we are done with the entire code - this returns immediately for all except the mirror
			}
			R6 = R6 + R1; // calculate address of letter to use
			R6 = [R6]; // the letter to use
			R4 = R4 + 0001; // increment the index
			R5 = R4 + 17f1; // index of new letter in code
			[R5] = R6; // set the letter
			R5 = [17f1]; // length of the code: twelve letters
		} while (R4 != R5); // loop until we've generated all the letters
	} while (!R3);
	print(17f1);
}
```

Re-implementing this in Python, we can now extract the code for the tablet directly from the binary!

Unfortunately, each of the other codes uses an `R0` based on the solution to the puzzle. In the case of the maze code:

    0f03 rmem R0 0e8e

The value at `0e8e` is derived from which rooms are visited in the maze, as mentioned in the main note file. Armed with our [trusty map](https://github.com/RunasSudo/synacor.py/blob/master/tools/graph.py), and cross-referencing the callbacks with the files, we identify:

* Twisty passages entrance, `0949`: Calls `0e9e`, resets `0e8e` to `0000`.
* West to `095d`: Calls `0ec0`: `OR`s `0e8e` with `0008`.
* South to `0926`: Calls `0eca`: `OR`s `0e8e` with `0010`.
* North to `096c`: Calls `0ede`: `OR`s `0e8e` with `0040`.

Putting it all together, the final value at `0e8e` is `0008 | 0010 | 0040` = `0058`.

Similarly, the `R0` for the teleporter code is the value of `R7` from the Ackermann function, which we determined earlier to be `6486`:

    1592 set  R0 R7

The remaining two codes, for the coins and the vault, are more complicated still, but follow the same pattern of determining `R0` based on the player's history.

For the coins, the call to `0731` derives an `R0` from the values at memory locations `69de` to `69e2`. One would presume that this relates to the order in which coins are inserted into the puzzle, and following the trail of callbacks for the coins confirms this. The important lines are:

    13c0 rmem R2 099e # nr of coins inserted
    13c3 add  R2 R2 69dd
    13c7 add  R2 R2 0001
    13cb wmem R2 R1 # R1 is the number of dots on the coin

Thus the values should be 9, 2, 5, 7 and 3: the missing numbers in the solved equation.

It is now trivial to generate the correct value of `R0`. Based on the code beginning, `15fd`:

```python
data_69de = [9, 2, 5, 7, 3]

R0 = 0
for i in range(len(data_69de)):
	R1 = data_69de[i]
	R0 = R0 + R1
	R0 = (R0 * 0x7bac) % 0x8000
	R0 = R0 ^ R1
```

The result is `0b3b`.

On to the final code, now: the vault lock. At `1679`, `R0` is computed as `([0f73] ^ [0f74]) ^ [0f75]`. Searching the code for references to these, we find:

    1236 wmem 0f70 0016 // weight
    1239 wmem 0f71 0000 // counter
    123c wmem 0f72 0000
    123f wmem 0f73 0000
    1242 wmem 0f74 0000
    1245 wmem 0f75 0000

It would be nice if these were just the intermediate weights of the orb, but alas the algorithm appears more complex than that.

Nevertheless, unravelling the various functions which reference those memory addresses:

```python
counter = 0
data_0f73 = 0
data_0f74 = 0
data_0f75 = 0

# 08c8
def rotatey_thing(R0, R1):
	while R1 != 0:
		R1 = (R1 + 0x7fff) % 0x8000
		R2 = R0 & 0x4000
		R0 = (R0 * 0x0002) % 0x8000
		if R2 == 0:
			continue
		R0 = R0 | 0x0001
	return R0

# 11a3
def mutate(R0val, R1, R2):
	return rotatey_thing(R0val, R1) ^ R2

# 1135
def update(value, room):
	global counter, data_0f73, data_0f74, data_0f75
	
	if counter <= 0x752f:
		counter += 1
	data_0f73 = mutate(data_0f73, counter + 2, room)
	data_0f74 = mutate(data_0f74, counter * counter, room * room)
	data_0f75 = mutate(data_0f75, 0x000d, (value * 9) * (value * 9))

update(0x0000, 0x0008) # north 1000
update(0x0004, 0x0009) # east 1011
update(0x0001, 0x000a) # east 1022
update(0x000b, 0x0006) # north 0fde
update(0x0002, 0x0005) # west 0fcd
update(0x0004, 0x0009) # south 1011
update(0x0001, 0x000a) # east 1022
update(0x0012, 0x000b) # east 1033
update(0x0001, 0x000a) # west 1022
update(0x000b, 0x0006) # north 0fde
update(0x0001, 0x0002) # north 0f98
update(0x0001, 0x0003) # east 0fa9
print(data_0f73)
print(data_0f74)
print(data_0f75)

result = (data_0f73 ^ data_0f74) ^ data_0f75

print('0x{:04x}'.format(result))
```

And with that, we can now [programmatically extract *every single code* given any challenge .tgz!](https://github.com/RunasSudo/synacor.py/blob/master/tools/generate_codes.py)
