import os
import re
import sys
from mmap import ACCESS_READ, mmap    
import ijson
import json
import glob
import nltk
from collections import defaultdict
from nltk.tokenize import sent_tokenize, word_tokenize
from bs4 import BeautifulSoup
import string

paths = [file for file in glob.glob(r"C:\Users\teehe\Desktop\DEV\**\*json")]

def generate_tokens(file):

    f = open(file, "r")
    #t = f.read().strip()
    loader = json.load(f)
    for words, value in loader.items():
        if words == "content":
            theText = ""
            soup = BeautifulSoup(value, "html.parser")
            for title in soup.find_all('title'):
                try:
                    theText += title.string
                except:
                    pass
            for bold in soup.find_all('b'):
                try:
                    theText += bold.string
                except:
                    pass
            for i in soup.find_all('strong'):
                theText += i.string

            for h in soup.find_all('h1', 'h2', 'h3'):
                theText += h.string
            text = soup.get_text()

    corpus = []
    for s in sent_tokenize(text):
        token_words = word_tokenize(s)
        # for t in token_words:
        #     if t.isalnum()==True:
        corpus += token_words
    print(corpus)




    #for file_name in [file for file in glob.glob(r"C:\Users\teehe\Desktop\DEV\**\*json")]:
        #for prefix, the_type, value in ijson.parse(open(file_name)):

            #if the_type == "content":
            #file_name = re.findall('><a href="(.*)">', prefix)
            #file_title = re.findall('<br><td> (.*)\n', value)
            #print(file_name)
            #ff = list(filter(None, (re.split((r"(\\[a-z])|[^a-z\\A-Z0-9]+"), value))))
            #soup = BeautifulSoup(value, 'html.parser')
            #print(x)
            #val = (json.loads(str(soup.text)))
            #val2 = str(val)
            #print(val2)
            #text = json.dumps(value)
            #text = soup.get_text(text)
            #text_tokens = word_tokenize(text)
            #print(prefix, the_type,value)

def main():
    for folder in paths:
        #print(folder)
        generate_tokens(folder)

if __name__ == "__main__":
    main()