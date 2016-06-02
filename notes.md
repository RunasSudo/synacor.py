# Spoilers!

Note: Codes seem to be unique for every user.

## The programming codes

### Code 1
Found in `arch-spec`.

    == hints ==
    - Here's a code for the challenge website: ............

### Code 2
Obtained on initial execution of code. (Or just be lazy like me and extract it from the binary.)

    Welcome to the Synacor Challenge!
    Please record your progress by putting codes like
    this one into the challenge website: ............

Required opcodes: `nop` and `out`

### Code 3
Obtained at the completion of the self-test.

    Executing self-test...
    
    self-test complete, all tests pass
    The self-test completion code is: ............

Required opcodes: All except `halt` and `in`

## The RPG codes

### Code 4 (Tablet)
At the foothills, the first area of the RPG:

    == Foothills ==
    Things of interest here:
    - tablet
    
    > take tablet
    
    > use tablet
    You find yourself writing "............" on the tablet.  Perhaps it's some kind of code?

Required opcodes: All except `halt`

### Code 5 (Twisty passages)
After falling down the bridge, there is an `empty lantern` to the `east`, which should be `take`n. To the `west`, there is a passage, where one can take the `ladder` down or venture into the `darkness`. Attempting to venture into the `darkness` at this point will result in being eaten by Grues.

Taking the `ladder` down, then traversing `west`, `south`, `north`, a code is obtained:

    Chiseled on the wall of one of the passageways, you see:
    
        ............
    
    You take note of this and keep walking.

There is also a can, which can be `take`n and `use`d to fill the lantern, which can then be `use`d to become lit, and which will keep away Grues.

### Code 6 (Dark passage, ruins and teleporter)
Returning to the fork at the passage and venturing to the `darkness`, we now `continue` `west`ward to the ruins. The `north` door is locked, but dotted elsewhere around the ruins are a `red coin` (2 dots), `corroded coin` (triangle = 3 sides), `shiny coin` (pentagon = 5 sides), `concave coin` (7 dots) and `blue coin` (9 dots) which should be `take`n and `look`ed at, and the equation:

    _ + _ * _^2 + _^3 - _ = 399

#### Mathematical!
In other words, we seek a solution to the equation *a* + *bc*<sup>2</sup> + *d*<sup>3</sup> - e = 399, where {*a*, *b*, *c*, *d*, *e*} = {2, 3, 5, 7, 9}.

Synacor being, of course, a programming-orientated exercise, the usual response to this problem is to code up a quick program to loop through all 5! = 120 permutations of the coins to find which one satisfies the equation. Being a mathematician, however – could you tell from the italics? – I will solve this the [*proper* way](https://xkcd.com/435/): with a scientific calculator and some thinking (\*insert insufferably smug expression here\*).

Firstly, note that -7 ≤ *a* − *e* ≤ 7, so 392 ≤ *bc*<sup>2</sup> + *d*<sup>3</sup> ≤ 406. Furthermore, since *bc*<sup>2</sup> is always positive, *d*<sup>3</sup> ≤ 406. We can thus rule out *d* = 9, so *d* ≤ 7, *d*<sup>3</sup> ≤ 343 and *bc*<sup>2</sup> ≤ 63, also ruling out *c* = 7 and *c* = 9. Furthermore, since 392 ≤ *bc*<sup>2</sup> + *d*<sup>3</sup>, *d*<sup>3</sup> ≥ 329. Since we already knew *d* ≤ 7, *d* = 7.

Consequently, 49 ≤ *bc*<sup>2</sup> ≤ 63. It is trivial to check that no solutions satisfy this for *c* = 2 and *c* = 3, so *c* = 5 and *b* = 2. The values of *a* and *e* are now easily found.

The solution is:

    9 + 2 * 5^2 + 7^3 - 3 = 399

**BOOM!**

(Well, actually all I did the first time was get up to *d* ≤ 7, then use guess and check.)

The coins should therefore be `use`d in the order: `blue`, `red`, `shiny`, `concave`, `corroded`.

Proceed to the `north` door and `use` the `teleporter` to obtain the code:

    == Ruins ==
    Things of interest here:
    - teleporter
    
    > use teleporter
    You activate the teleporter!  As you spiral through time and space, you think you see a pattern in the stars...
    
        ............
    
    After a few moments, you find yourself back on solid ground and a little disoriented.

## The true-believers-only codes
At this point, you will almost certainly need to delve into the code of the challenge, if you haven't already. The code in `challenge.bin` past the self-test is encrypted, so disassembling and analysing the code is most easily done based off a memory dump from a running copy.

### The guts
(Note to self: `pop` takes an operand, *duh*. No wonder everything looked funny…)

Note that at `1808` there is the following data:

    1808 data 00b7
    1809 data "You find yourself standing at the base of an enormous mountain. ...

(Accompanied by some other familiar-sounding but somewhat garbled strings.) Searching the code for references to `1809` yields nothing, but searching for `1808` yields the following as the only result:

    090d data 17fe 1808 6914 6917
    0911 halt # (i.e. data 0000)

The first address referred to in the `090d` line has value `0009`, which looks suspiciously like a length. Indeed, this is the exact length of the following string `Foothills`. Continuing in this manner,

    17fe data 0009 "Foothills"
    1808 data 00b7 "You find yourself standing at the base of an enormous mountain. ...
    6914 data 0002 18c0 18c8
    6917 data 0002 0917 0912

Following the rabbit hole,

    18c0 data 0007 "doorway"
    18c8 data 0005 "south"
    0917 data 1929 1933 691e 6921 0000
    0912 data 18ce 18d8 691a 691c 0000

And unsurprisingly, the `0912` line leads to the data for the screen reached when venturing `south` from the beginning.

Scrolling through the list of rooms beginning `090d`, we notice a peculiarly long line, `0949`:

    0949 data
              1fe3 # -> string "Twisty passages"
              1ff3 # -> string "You are in a maze ...
              695b # -> data 0005 206f 2076 207c 2082 2087
              6961 # -> data 0005 093f 094e 0953 0958 095d

So far so good, but what's this??

              0e9e # -> wmem 0e8e 0000; ret
              208c # -> string "Twisty passages"
              209c # -> string "You are in a twisty maze ...
              ...

Aah, so it looks like each room is stored as a block of 5 words, each a pointer to a length of words: a string (the title), a string (the text), a list of pointers to strings (the exit names), a list of pointers to more rooms (the exits), and a memory location to `call` (or `0000`).

Further analysis suggests that this particular call relates to the step counter for the Grues in the maze.

We probably could have reached these same conclusions by analysing the suspicious-looking block of code following the room definitions, but assembly makes my head spin so ¯\_(ツ)_/¯

Now what about items? Looking at a more familiar item, the tablet:

    0a6c data 468e 4695 090d 1270
    468e data 0006 "tablet"
    4695 data 0088 "The tablet seems appropriate for use as a writing surface but is unfortunately blank.  Perhaps you should USE it as a writing surface..."
    090d ... # the foothills from earlier
    1270 ... # a subroutine that presumably prints code 4

### Code 7 (Synacor Headquarters and Teleporter 2: Electric Boogaloo)

Examining the data for the teleporter:

    0a94 data 4a55 4a60 099f 1545
    4a55 data 000a "teleporter"
    4a60 data 0048 "This small device has a button on it and reads \"teleporter\" on the side."
    099f ... # the north room in the ruins
    1545 ... # aha!

Now, let's see what this `1545` does. C-style, because assembly makes my brain spin.

```c
1545() {
	if (R8 == 0)
		return 15e5(); // Ground state teleport
	05b2(70ac, 05fb, 1807 + 585a); // Secure text print
	for(i = 0; i < 5; i++); // Speed up loop, because why not?
	
	if (178b(0004, 0001) != 0006) // The check!
		return 15cb();
	
	05b2(7156, 05fb, 1ed6 + 0992);
	
	0731(R8, 650a, 7fff, 7239);
	
	05b2(723d, 05fb, 7c1f + 0146);
	
	mem[0aac] = 09c2;
	mem[0aad] = 0000;
	
	mem[0a94 + 0002] = 7fff;
	
	return 1652();
}

178b(R1, R2) {
	if (R1 != 0) {
		return 1793(R1, R2);
	}
	return R2 + 0001;
}

1793(R1, R2) {
	if (R2 != 0) {
		return 17a0(R1, R2);
	}
	R1 = R1 + 7fff;
	R2 = R8;
	R1 = 178b(R1, R2);
	return R1;
}

17a0(R1, R2) {
	R2 = R2 + 7fff;
	R2 = 178b(R1, R2);
	R1 = R1 + 7fff;
	R1 = 178b(R1, R2);
	return R1;
}
```

Phew, so in other words, we seek an `R8` such that `178b(4, 1, R8)` equals 6. Let's see if we can't rewrite that function. Note that adding 0x7fff = 32767 to a number modulo 32768 is equivalent to subtracting 1. Thinking through the code, then,

    A(R1, R2) = R2 + 1                   , if R1 = 0
                A(R1 - 1, R8)            , if R1 ≠ 0 and R2 = 0
                A(R1 - 1, A(R1, R2 - 1)) , if R1 ≠ 0 and R2 ≠ 0

Recognise anything? Well, neither did I the first time, and I'd [already seen the video](https://www.youtube.com/watch?v=i7sm9dzFtEI). It's the [Ackermann function](https://en.wikipedia.org/wiki/Ackermann_function)! With the slight twist that instead of the second line being `A(R1 - 1, 1)`, it's `A(R1 - 1, R8)`.

No mathematical wizardry here, just implementing this and run a brute-force on all possible values of `R8`. And as much as it pains me to admit this, this is a tool for the raw processing efficiency of C, which I am not very proficient in, so I based my solution on [this wonderful code](https://github.com/glguy/synacor-vm/blob/master/teleport.c) by [glguy](https://github.com/glguy). My only contribution is the parallelisation of the computation. (500% speed-up! Whoo!)

    gcc ackermann.c -o ackermann -lpthread -O3 && ./ackermann

Running the algorithm, the correct value is revealed to be `0x6486`.

### Code 8 (Beach and vault)
