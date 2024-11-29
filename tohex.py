#! /usr/bin/env python3

import sys
import os

BLKLEN = 16


def main(argv):
    if len(argv) != 3:
        tohex = os.path.basename(argv[0] if len(argv) > 0 else "tohex")
        print(f"Usage:    {tohex} <fromfile> <tofile>")
        return 2

    with open(argv[1], "rb") as srcf, open(argv[2], "w", newline="\r\n") as dstf:
        while True:
            bff = srcf.read(BLKLEN)
            if len(bff) == 0:
                break

            dstf.write(":")
            dstf.write(bff.hex().upper())
            dstf.write("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
