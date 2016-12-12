#CMTEST.py
#A test file to see how command line inputs are passed

import sys
import argparse

"""

Here are the things that need to be passed to the parser

story = 'none' #'none', 'summary' and 'verbose' are OK answers. -n, -s, -v?
outfile = 'Test.txt' #output file - doesn't do anything right now...can wait on this
maxrounds = 100 #set low if you want to break up the combat, set high to fight to the death
MOSC = 50 #number of monte carlos
HPHR = 0.5 #hit point fraction at which point they seek healing
critrule = 1 #which critical damage rule will be used (see critdam() for more)

https://docs.python.org/3/library/argparse.html
"""

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('integers', metavar='N', type=int, nargs='+',
...                     help='an integer for the accumulator')

parser.add_argument('--sum', dest='accumulate', action='store_const',
...                     const=sum, default=max,
...                     help='sum the integers (default: find the max)')
