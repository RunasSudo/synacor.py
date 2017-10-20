# synacor.py

My OOP, ~~poorly-documented~~ ~~concise~~ working response to the Synacor challenge

## Debug commands

At any time the program is waiting for input, a string of the following form may be input:

    .<cmd> <args>

This will execute the file `<cmd>.py` with `dbg_args[0]` set to `<cmd>` and `<args>` stored in `dbg_args[1..n]`.

For example, the self-test and decryption at the beginning of the program takes a comparatively long time. To save the state to the `dumps/init` file, enter:

    .dbg/dump dumps/init

Similarly, debug commands may be passed as command-line arguments to `synacor.py` in the form:

    ./synacor.py <file> <cmd> <args>

For example, to load the `dumps/init` state to skip the self-test and decryption, run:

    ./synacor.py challenge.bin dbg/load dumps/init

Dump files are stored in Python [pickle](https://docs.python.org/3/library/pickle.html) format, so if you want to inspect the memory in a hex editor, for example, it will be necessary to extract a raw memory dump:

    ./tools/dump_to_raw.py dumps/init dumps/init.raw
