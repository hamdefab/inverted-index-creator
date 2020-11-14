import os
import re
import sys
from mmap import ACCESS_READ, mmap    
import ijson
import os
import json
import glob
import nltk
from collections import defaultdict
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import snowball
from pathlib import Path
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


    #stemming = snowball.SnowballStemmer('english')
    text = text.lower()
    # for docid, c in enumerate(text):
    #     for s in sent_tokenize(text):
    #         token_words = word_tokenize(s)
    #         stem = stemming.stem(str(token_words))
    #         inverted_index[token_words].add(docid)
    #
    #         #corpus += token_words
    for s in sent_tokenize(text):
        token_words = word_tokenize(s)
        corpus += token_words

    # for docid, c in text:
    #     for sent in sent_tokenize(c):
    #         for word in word_tokenize(sent):
    #             word_lower = word.lower()
    #             word_stem = stemming.stem(word_lower)
    #             inverted_index[word_stem].add(docid)

    # for item in corpus:
    #     inverted_index = {}
    #     with open("inverted_index.txt", 'w')as index:
    #         inverted_index = json.load(index)
    #     if item not in inverted_index:
    #         inverted_index[item] = 1
    #     if item in inverted_index:
    #         inverted_index[item] += 1
    #     with open("inverted_index.txt", 'w')as index:
    #         index.write(json.dumps(inverted_index))

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
            file2.seek(0)
            lines = file2.readlines()
            for line in lines:
                if tokens[token] == line.strip("\n"):
                    in_file = True
            if in_file == False:
                file2.write(tokens[token] + "\n")

    file2.seek(0)
    length = len(file2.readlines())

    file1.close()
    file2.close()
    return length

def main():
    count = 0
    for folder in paths:
        #print(folder)
        corpus = generate_tokens(folder)
        length_of_unique = reportFunc(corpus)
        count+= 1
    report = open("report.txt", "a+", encoding="utf-8")
    report.write("Number of Indexed Documents: " + count + "\n")
    report.write("The number of unique word: " + length_of_unique + "\n")

if __name__ == "__main__":
    main()