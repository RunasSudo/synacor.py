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
  * Since only `R1` and `R2` are checked, this would not detect errors involving other registers.
  * This test, like the last one, reuses the results of previous tests, since that worked out so well for `eq`…
* `0264` to `0276`: Tests `gt`
  * The tests performed seem quite reasonable, but yet again reuse the results of previous tests…
* `0279` to `02ab`: Tests `and` and `or`
  * Confusingly, the error handling is located in different places for each test.
* `02ac` to `02bd`: Tests `not`
  * Okay, I admit this one was pretty helpful. What the hell is a ‘15-bit bitwise inverse’? Well the test passes if I do just do mod 32768, so that works I guess…
* `02c0` to `02e8`: Tests `call`
  * Although, notably, not `ret`. The tests operates by `jmp`ing back and forth to test the various values of `R1`.
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

    06bb push R1
    06bd push R2
    06bf set  R2 17b4
    06c2 rmem R1 R2
    06c5 push R2
    06c7 mult R2 R2 R2
    06cb call 084d
    06cd set  R2 4154
    06d0 call 084d
    06d2 pop  R2
    06d4 wmem R2 R1
    06d7 add  R2 R2 0001
    06db eq   R1 7562 R2
    06df jf   R1 06c2
    06e2 pop  R2
    06e4 pop  R1
    06e6 ret

Inspecting the `084d` subroutine reveals that this is simply an XOR function: `R1 XOR R2`. Crypto rating: 1/10

Rewriting `06bb` function using higher-level syntax reveals that the ‘encryption’ algorithm is really very simple:

```c
06bb() {
	R2 = 17b4;
	for (R2 = 17b4; R2 != 7562; R2++) {
		R1 = [R2];
		R1 ^= R2 * R2;
		R1 ^= 4154;
		[R2] = R1;
	}
}
```

*Very* simple.

[By emulating this function in Python](https://github.com/RunasSudo/synacor.py/blob/master/dbg_fastboot.py), we can skip the self-test and computationally-expensive decryption process entirely, and get straight into the good stuff next time we want to play!

## Encrypted strings

So earlier, we produced a tool-assisted speed-run that would complete and dump the codes for any given challenge binary, but where's the fun in that? Why not extract the codes from the binary directly? Of course, this is easier said than done. None of the codes, nor any of the strings relating to them, are visible in the disassembled binary, whether before or after the decryption from the previous section.

Looking through the code following the self-test, we find:

    0413 set  R1 17c0
    0416 call 05ee

Digging deeper, `05ee` calls `05b2` with `R2` set to `05f8`. `05b2` appears to iterate over the characters in a string whose length is stored in address `R1`, and calls `R2` for each character, storing the character in `R1`. `05f8` (the callback provided by `05ee`) simply outputs every character in `R1` it gets.

Immediately after this call to `05ee`, we find:

    041e set  R1 68e3
    0421 set  R2 05fb
    0424 add  R3 XXXX XXXX
    0428 call 05b2

In other words, a similar string-handling subroutine is called, but instead of `05f8` (which would simply print the string), `05fb` is called. `05fb` also outputs the character, but only after calling `084d` (XOR) with `R2` set to `R3`.

Now we have everything we need to [extract these encrypted (double-encrypted??) strings](https://github.com/RunasSudo/synacor.py/blob/master/tools/decrypt_strings.py) from the binary!

Only the self-test completion code appears to be stored there, though, so I'm not sure what the point of encrypting those was…
