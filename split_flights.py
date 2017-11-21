"""
Flights are returned as a single JSON blob but really want them
line by line.
"""

from __future__ import unicode_literals, print_function

import json
import argparse
import io
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('infiles', nargs='+')
    return parser.parse_args()


def main():
    args = parse_args()

    for infile in args.infiles:
        if not infile.endswith('.json'):
            print(infile, 'missing json suffix - skipping')
            continue

        outfile = infile[:-5] + '.ndjson'
        with io.open(infile) as fin, io.open(outfile, 'wb') as fout:
            data = json.load(fin)
            states = data['states']
            for state in states:
                json.dump(state, fout)
                fout.write(os.linesep)


if __name__ == '__main__':
    main()
