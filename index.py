import re
import sys
from mmap import ACCESS_READ, mmap    

def generate_tokens(filename, pattern):
    with open(filename) as f, mmap(f.fileno(), 0, access=ACCESS_READ) as mm:
         yield from re.finditer(pattern, mm)