import os
import re
import sys
from mmap import ACCESS_READ, mmap
import ijson
import json
import time
import glob
import nltk
import pickle
from nltk.stem import PorterStemmer
from collections import defaultdict
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import snowball
from pathlib import Path
from bs4 import BeautifulSoup
import string

paths = [file for file in glob.glob(r"/Users/nicholasjaber/PycharmProjects/inf141/assignment 3/DEV/**/*json")]

def generate_tokens(file):
    f = open(file, "r")
    loader = json.load(f)
    for words, value in loader.items():
        if words == "content":
            theText = ""
            soup = BeautifulSoup(value, "html.parser")
            for h in soup.find_all('h1', 'h2', 'h3', 'b', 'title'):
                theText += h.string + " " + h.string + " " + h.string
            for h in soup.find_all('p'):
                try:
                    theText += h.string
                except:
                    pass
            text = soup.get_text()
    corpus = []
    punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~©'''

    text = text.strip(punc)
    text = text.lower()
    ps=PorterStemmer()
    for s in sent_tokenize(text):
        token_words = word_tokenize(s.lower())
        temp=[]
        for token in token_words:
            temp.append(ps.stem(token).strip(punc))
        corpus += temp
    return corpus



def reportFunc(tokens,count):

    file2 = open("file2.txt", "a+" , encoding ="utf-8")
    tokens = " ".join(tokens)

    in_file = False
    lines = file2.readlines()
    for token in range(len(''.join(tokens).split(" "))):
        temp = ''.join(tokens).split(" ")
        for line in lines:
            if temp[token] == line.strip("\n"):
                in_file = True
        if in_file == False and '-' not in temp[token] and ',' not in temp[token]:
            file2.write(temp[token] + "\n")
    file2.seek(0)
    length = len(file2.readlines())
    file2.close()
    file2 = open('file2.txt','r', encoding ="utf-8")
    uniqe_words = file2.readlines()
    file2.close()
    inverted_index = {}
    my_file = Path(r"/Users/nicholasjaber/PycharmProjects/inf141/assignment 3/inverted_index.txt")

    if my_file.is_file():
        with open("inverted_index.txt", encoding ="utf-8") as f:
            inverted_index = eval(f.read())
    for unique in uniqe_words:
        temp = unique.strip('\n').strip(' ')
        if temp in inverted_index and tokens.count(temp)!=0:
            set_tup= inverted_index[temp]
            set_tup.add((tokens.count(temp),count))
            inverted_index[temp] = set_tup
        elif tokens.count(temp)!=0:
            set_tup={(tokens.count(temp),count)}
            inverted_index[temp] = set_tup
    with open('inverted_index.txt', "w", encoding ="utf-8") as data:
        data.write(str(inverted_index))
    print(count)
    return length

def search(query,tot_count):
    max_tup=(0,0)
    ps = PorterStemmer()
    tokens = query.split(' ')
    stems = []
    inverted_index = {}
    for token in tokens:
        stems.append(ps.stem(token))
    with open('inverted_index.txt', "r", encoding ="utf-8") as f:
        inverted_index = eval(f.read())
    max_tups = []
    stem_set_list = []
    for i in stems:
        if i in inverted_index:
            stem_set_list.append(list(inverted_index[i]))
    for current_count in range(tot_count):
        started_file = False
        for i in stem_set_list: #takes sets from inverted index that are in inverted index casts as list now we iterate through those
            temp = [lis for lis in i if lis[1]==current_count] #gives u whatever tuples in i at file current_count
            if len(temp)!=0 and started_file==False:
                max_tups.extend(temp)
                started_file=True
            elif len(temp)!=0:
                max_tups[-1] = (int(max_tups[-1][0])+int(temp[0][0]),temp[0][1])
    file_json = open('json_files.txt', 'r', encoding ="utf-8")
    for i in sorted(max_tups, reverse=True)[:5]:
        file_json.seek(0)
        output = file_json.readlines()[i[1]]
        print(i[0], output.split("/")[-1])
    file_json.close()

def make_all_files_count():
    file_json = open('json_files.txt','w', encoding ="utf-8")
    for i in paths:
        file_json.write(i + "\n")
    file_json.close()

def main():
    run_type = input('r/s: ')
    if run_type =='s':
        inverted_index = {}
        with open('inverted_index.txt', "r") as f:
            inverted_index = eval(f.read())
        make_all_files_count()
        start_time =time.time()
        search(input('query: '),24)
        end_time = time.time()
        print(end_time-start_time)
    elif run_type=='r':
        count = 0
        length_of_unique = 0
        for folder in paths:
            corpus = generate_tokens(folder)
            length_of_unique = reportFunc(corpus,count)
            count += 1
    else:
        main()


if __name__ == "__main__":
    main()