import re
import sys
from mmap import ACCESS_READ, mmap    
import ijson
import glob

def generate_tokens():
    # with open(filename) as f, mmap(f.fileno(), 0, access=ACCESS_READ) as mm:
    #     yield from re.finditer(pattern, mm)cd hw2
    for file_name in [file for file in glob.glob("~/cs121/hw3/DEV/*/.JSON")]:
        for prefix, the_type, value in ijson.parse(file_name)):
            print (prefix, the_type, value)

def main():
    

if __name__ == "__main__":
    main()