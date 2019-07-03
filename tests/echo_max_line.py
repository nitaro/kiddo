#!/usr/bin/python 3

import sys

max = int(sys.argv[-1]) + 1
for i in range(max):
    if i == max - 1:
        sys.stdout.write("{}".format(i))
    else:
        print("debug:", i)

sys.exit()