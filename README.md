# synacor.py

My sort-of-OOP, ~~poorly-documented~~concise response to the Synacor challenge

## Debug commands

At any time the program is waiting for input, a string of the following form may be input:

    .<cmd> <args>

This will execute the file `<cmd>.py` with `dbg_args[0]` set to `<cmd>` and `<args>` stored in `dbg_args[1..n]`.

For example, the self-test and decryption at the beginning of the program takes a comparatively long time. To save the state to the `dumps/init` file, enter:

    .dbg_dump dumps/init

Similarly, debug commands may be passed as command-line arguments to `synacor.py` in the form:

    ./synacor.py <cmd> <args>

For example, to load the `dumps/init` state to skip the self-test and decryption, run:

    ./synacor.py dbg_load dumps/init
