#! /usr/bin/env python3

import sys
import os

from pathlib import Path

LINES_PER_FILE = 1350


def main(argv):
    if len(argv) != 2:
        splithex = os.path.basename(argv[0] if len(argv) > 0 else "splithex")
        print(f"Usage:    {splithex} <file>")
        return 2

    src_path = Path(argv[1])
    with open(src_path) as srcf:
        i_name = 1
        dstf = open(src_path.with_stem(f"{src_path.stem}{i_name}"), "w", newline="\r\n")
        for i, line in enumerate(srcf):
            dstf.write(line)
            if ((i + 1) % LINES_PER_FILE) == 0:
                dstf.close()
                i_name += 1
                dstf = open(
                    src_path.with_stem(f"{src_path.stem}{i_name}"), "w", newline="\r\n"
                )

        dstf.close()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
