from __future__ import print_function
import sys


if __name__ == '__main__':
    try:
        while True:
            line = raw_input()
            print('+++ ' + line)
            print('!!! ' + line, file=sys.stderr)
            sys.stdout.flush()
            sys.stderr.flush()

    except KeyboardInterrupt:
        print('### exiting...', file=sys.stderr)
