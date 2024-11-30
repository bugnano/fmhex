#! /usr/bin/env python3

import sys
import os

from pathlib import Path

#
# BOO Encoder Options
#

# max output chars per line
MAXOUTLEN = 72

# max null compression via ~
MAXNULLCOMP = 78

# min of 2 nulls to compress
MINNULLCOMP = 2


def tochar(n):
    return chr(n + ord("0"))


def main(argv):
    if len(argv) != 3:
        toboo = os.path.basename(argv[0] if len(argv) > 0 else "toboo")
        print(f"Usage:    {toboo} <fromfile> <tofile>")
        return 2

    src_path = Path(argv[1])
    with open(argv[1], "rb") as srcf, open(argv[2], "w", newline="\r\n") as dstf:
        # first line in output file is filename
        dstf.write(src_path.name)
        dstf.write("\n")

        old_remainder = b""
        outbuf = ""
        fill_nulls = 0

        while True:
            (inbuf, nulls, remainder) = get3(srcf, old_remainder)
            if (inbuf, nulls, remainder) == (b"", 0, b""):
                break

            if nulls > 0:
                # bunch of nulls
                outbuf = f"~{tochar(nulls)}"
            else:
                fill_nulls = 3 - len(inbuf)
                inbuf = (inbuf + b"\0\0\0")[:3]
                outbuf = boo(inbuf)

            output(dstf, outbuf)

            old_remainder = remainder

        if fill_nulls > 0:
            output(dstf, "~0" * fill_nulls)

        dstf.write("\n")

    return 0


def get3(fp, old_remainder):
    buf = old_remainder
    remainder = b""
    i = len(buf) if buf != b"\0" else 0
    nulls = 0 if buf != b"\0" else 1

    while True:
        c = fp.read(1)
        if len(c) == 0:
            break

        if (c != b"\0") and (nulls > 0):
            # stop collecting
            if nulls < MINNULLCOMP:
                # correct for too few nulls
                # nulls + new char
                i = nulls + 1
                # restore null data
                buf += b"\0" * nulls
                # store curr char
                buf += c
                nulls = 0
            else:
                # save non-null
                remainder = c
                break
        elif (c == b"\0") and (i == 0):
            # collect
            nulls += 1
        else:
            # count till 3
            i += 1
            # save chars
            buf += c

        if (i > 2) or (nulls > MAXNULLCOMP):
            break

    if nulls > MAXNULLCOMP:
        # save the 79th null for next time
        remainder = b"\0"

    return (buf, nulls, remainder)


outlen = 0


# output chars taking care of line wraps
# we are keeping output quads on the same line
def output(fp, buf):
    global outlen

    if (outlen + len(buf)) > MAXOUTLEN:
        fp.write("\n")
        outlen = 0

    fp.write(buf)
    outlen += len(buf)


# here is where we boo 3 into 4 chars
def boo(inbuf):
    # get x,y,z the 3 input bytes
    x = inbuf[0]
    y = inbuf[1]
    z = inbuf[2]

    # generate a,b,c,d the 4 output bytes
    a = x >> 2
    b = ((x << 4) | (y >> 4)) & 0o77
    c = ((y << 2) | (z >> 6)) & 0o77
    d = z & 0o77

    outbuf = "".join(map(tochar, [a, b, c, d]))

    return outbuf


if __name__ == "__main__":
    sys.exit(main(sys.argv))
