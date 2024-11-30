# Accessing a DOS machine without floppy

While researching on how to send files to a DOS machine via serial port,
I stumbled upon this website:

https://jcoppens.com/soft/howto/bootstrap/index.en.php

This was interesting but I had 2 problems with that:

1. QBasic is only available from MS-DOS version 5 onwards.
   My Olivetti M24 has MS-DOS 3.3, so I couldn't use the QBasic program provided.
2. The QBasic program does not work if the hex file is larger than 64k.

So I rewrote the program in GW-BASIC and removed the 64k limitation.

While I was at it, I also rewrote the binary to hex converter in Python, so
that it's easier to run on modern Linux systems.

While continuing the research, I stumbled upon the BOO file format from The
Kermit Project:

https://www.columbia.edu/kermit/archivefiles/boo.html

which is an encoding similar to Base64, that encodes 3 bytes into 4 printable
ASCII characters, and implements a rudimentary RLE compression on consecutive
NUL bytes.

In particular the `msbpcg.com` file caught my attention.
It is a DOS COM executable, but consisting only of printable ASCII characters,
that decodes BOO files.

While I was at it, given that the program to encode BOO files is written in
pre-standard C, I rewrote it in Python, so that it's easier to run on modern
Linux systems.

## The problem

MS-DOS does not have a serial communication program included, but if the only
choice we have to communicate with the DOS machine is the serial port, how do
we put the serial communication program on the DOS machine?

Luckily on DOS it is still possible to transfer small **text** files via the
serial port (by small I mean under 64k), with a baud rate of at most 9600bps.

Now we have a problem:
The serial communication program is a **binary** file, but we can only send
text files.

## Solution 1: HEX files

Here's where `tohex.py` comes into play: it converts a binary file to its hex
representation, generating a text file.

Note that if the generated text file is bigger than 64k, transferring it to
the DOS machine could fail, so it's better to split it on chunks of less than
64k, ideally splitting it at the end of the line.
I've included the `splithex.py` program that splits the hex file every 1350
lines, resulting in files of about 46k.

After that, we can send the hex file(s) to the DOS machine.

Now we have another problem:
We need to reconstruct the binary file on the DOS machine, as it cannot
execute the hex files directly.

Here's where `fmhex.bas` comes into play: it converts a hex file to binary.
Being written in GW-BASIC, it is compatible with any MS-DOS version, as MS-DOS
versions prior to 5 include GW-BASIC, and versions 5 and above include QBasic,
which is compatible with GW-BASIC source files.

### How to use

Let's say that we want to transfer the `ZM.EXE` file to the DOS machine.

First of all, we need to convert it to hex, so, from our Linux machine we run:

```bash
python3 tohex.py ZM.EXE zm.hex
```

Now the problem is that `zm.hex` is about 92k, so it's too big to be
transferred as-is. We need to split it, so we need to run:

```bash
python3 splithex.py zm.hex 1350
```

This creates the files `zm1.hex` and `zm2.hex`.

Now we're ready to send the files to the DOS machine.

After connecting the DOS machine to the Linux machine with a null-modem cable,
from the DOS machine we need to setup the serial port for 9600 baud, no
partiy, 8 bit data, 1 stop bit:

```dos
mode com1:9600,n,8,1,p
```

From the Linux machine we need to use a serial communication program to
transfer the file to the DOS machine. In this example we'll use `minicom`:

```bash
minicom -b 9600 -D /dev/ttyUSB0
```

After that we need to prepare the DOS machine to receive the first file:

```dos
copy com1: zm1.hex
```

To transfer the file, from the Linux machine press `CTRL-A` followed by `S`,
then select `ascii` as the file transfer method, then select the file
`zm1.hex`.

After the transfer has been completed, we need to tell the DOS machine that
the file transfer has been completed, so from our Linux machine, press
`CTRL-Z`.

Repeat the procedure for the `zm2.hex` and `fmhex.bas` files, starting from
the `copy` command on the DOS machine.

After all files have been transferred, we need to reconstruct the `zm.hex`
file from the 2 splitted files, so from the DOS machine run:

```dos
copy zm1.hex+zm2.hex zm.hex
```

And now we can reconstruct the binary file:

```dos
gwbasic fmhex.bas
```

Of course, if you're running MS-DOS version 5 or above, substitute `gwbasic`
with `qbasic`.

Type `zm.hex` for the input archive and `zm.exe` for the output archive.

Note that it might seem that the DOS machine has frozen, but be patient.
On an Olivetti M24 reconstructing the `zm.exe` file takes about 10 minutes.

After that, we can use the `zm.exe` file to transfer files at higher baud
rates and reliably, using the Zmodem protocol.

## Solution 2: BOO files (recommended)

Here's where `toboo.py` comes into play: it converts a binary file to the BOO
format, which is a text file.

Note that if the generated text file is bigger than 64k, transferring it to
the DOS machine could fail, so it's better to split it on chunks of less than
64k, ideally splitting it at the end of the line.
I've included the `splithex.py` program that splits the BOO file every 800
lines, resulting in files of about 57k.
Refer to Solution 1 on how to use `splithex.py`, and substitute 1350 with 800.

After that, we can send the BOO file(s) to the DOS machine.

Now we have another problem:
We need to reconstruct the binary file on the DOS machine, as it cannot
execute the BOO files directly.

Here's where `msbpcg.com` comes into play: it converts a BOO file to binary.
Being a DOS COM executable consisting only of printable ASCII characters,
it can easily be transferred like the other text files, and it can be directly
executed on the DOS machine.

### How to use

Let's say that we want to transfer the `ZM.EXE` file to the DOS machine.

First of all, we need to convert it to BOO, so, from our Linux machine we run:

```bash
python3 toboo.py ZM.EXE zm.boo
```

The resulting `zm.boo` file is about 57k, so it's OK to be transferred in a
single shot.

After connecting the DOS machine to the Linux machine with a null-modem cable,
from the DOS machine we need to setup the serial port for 9600 baud, no
partiy, 8 bit data, 1 stop bit:

```dos
mode com1:9600,n,8,1,p
```

From the Linux machine we need to use a serial communication program to
transfer the file to the DOS machine. In this example we'll use `minicom`:

```bash
minicom -b 9600 -D /dev/ttyUSB0
```

After that we need to prepare the DOS machine to receive the first file:

```dos
copy com1: zm.boo
```

To transfer the file, from the Linux machine press `CTRL-A` followed by `S`,
then select `ascii` as the file transfer method, then select the file
`zm.boo`.

After the transfer has been completed, we need to tell the DOS machine that
the file transfer has been completed, so from our Linux machine, press
`CTRL-Z`.

Repeat the procedure for the `msbpcg.com` file, starting from the `copy`
command on the DOS machine.

After all files have been transferred, we can reconstruct the binary file:

```dos
msbpcg zm.boo
```

After that, we can use the `zm.exe` file to transfer files at higher baud
rates and reliably, using the Zmodem protocol.

## License

Unlicense

