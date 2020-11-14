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

paths = [file for file in glob.glob(r"C:\Users\hamza\OneDrive\Desktop\DEV\**\*json")]

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
    punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~©'''
    for each in text:
        if each in punc:
            text = text.replace(each," ")

    for s in sent_tokenize(text):
        token_words = word_tokenize(s)
        # for t in token_words:
        #     if t.isalnum()==True:
        corpus += token_words
    return corpus

def reportFunc(tokens):
    file1 = open("file1.txt", "a+" , encoding ="utf-8")
    file2 = open("file2.txt", "a+" , encoding ="utf-8")
    for token in range(len(tokens)):
        if token + 6 < len(tokens):
            file1.write(tokens[token] + " ")
            file1.write(tokens[token + 1] + " ")
            file1.write(tokens[token + 2] + " ")
            file1.write(tokens[token + 3] + " ")
            file1.write(tokens[token + 4] + " " + "\n")
            in_file = False
            for line in file2.readlines():
                if tokens[token] == line:
                    in_file = True
            if in_file == False:
                file2.write(tokens[token] + "\n")
    #os.path.getsize()

def main():
    count = 0
    for folder in paths:
        #print(folder)
        corpus = generate_tokens(folder)
        reportFunc(corpus)
        count+= 1

if __name__ == "__main__":
    main()