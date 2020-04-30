import gzip
import bz2
import itertools
import sys

def open_compressed(filename, mode='rb'):
    if filename.endswith('.gz'):
        return gzip.open(filename, mode)
    elif filename.endswith('.bz2'):
        return bz2.open(filename, mode)
    elif filename == '-':
        if 'r' in mode:
            if 'b' in mode:
                return sys.stdin.buffer
            else:
                return sys.stdin
        elif 'w' in mode:
            if 'b' in mode:
                return sys.stdout.buffer
            else:
                return sys.stdout
    else:
        return open(filename, mode=mode)

def batches(it, batch_size):
    it = iter(it)
    return iter(lambda: tuple(itertools.islice(it, batch_size)), ())
