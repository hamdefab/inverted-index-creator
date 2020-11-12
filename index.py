import json
import re
import string
import sys
from mmap import ACCESS_READ, mmap    
import ijson
import glob
import nltk
from collections import defaultdict
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import snowball
nltk.download('punkt')

def generate_tokens():
    punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''

    for file_name in [file for file in glob.glob(r"C:\Users\hamza\OneDrive\Desktop\DEV\**\*json")]:
        for url, encoding, content in ijson.parse(open(file_name)):
            text = json.dumps(content)
            text_tokens = word_tokenize(text)
            # for each in text_tokens:
            #     if each in punc:
            #         text_tokens = text_tokens.filter(each)
            print(text_tokens)

def main():
   generate_tokens()

if __name__ == "__main__":
    main()