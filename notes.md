# Spoilers!

Note: Codes seem to be unique for every user.

## Code 1
Found in `arch-spec`.

    == hints ==
    - Here's a code for the challenge website: ............

## Code 2
Obtained on initial execution of code. (Or just be lazy like me and extract it from the binary.)

    Welcome to the Synacor Challenge!
    Please record your progress by putting codes like
    this one into the challenge website: ............

Required opcodes: `nop` and `out`

## Code 3
Obtained at the completion of the self-test.

    Executing self-test...
    
    self-test complete, all tests pass
    The self-test completion code is: ............

Required opcodes: All except `halt` and `in`

## Code 4
At the foothills, the first area of the RPG:

    == Foothills ==
    Things of interest here:
    - tablet
    
    > take tablet
    
    > use tablet
    You find yourself writing "............" on the tablet.  Perhaps it's some kind of code?

Required opcodes: All except `halt`

## Code 5 (Twisty passages)
After falling down the bridge, there is an `empty lantern` to the `east`, which should be `take`n. To the `west`, there is a passage, where one can take the `ladder` down or venture into the `darkness`. Attempting to venture into the `darkness` at this point will result in being eaten by Grues.

Taking the `ladder` down, then traversing `west`, `south`, `north`, a code is obtained:

    Chiseled on the wall of one of the passageways, you see:
    
        ............
    
    You take note of this and keep walking.

There is also a can, which can be `take`n and `use`d to fill the lantern, which can then be `use`d to become lit, and which will keep away Grues.

## Code 6 (Dark passage, ruins and teleporter)
Returning to the fork at the passage and venturing to the `darkness`, we now `continue` `west`ward to the ruins. The `north` door is locked, but dotted elsewhere around the ruins are a `red coin` (2 dots), `corroded coin` (triangle = 3 sides), `shiny coin` (pentagon = 5 sides), `concave coin` (7 dots) and `blue coin` (9 dots) which should be `take`n and `look`ed at, and the equation:

    _ + _ * _^2 + _^3 - _ = 399

### Mathematical!
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
