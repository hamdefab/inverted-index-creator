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

paths = [file for file in glob.glob(r"C:\Users\hamza\OneDrive\Desktop\DEV\**\*json")]

def generate_tokens(file):
    f = open(file, "r")
    loader = json.load(f)
    for words, value in loader.items():
        if words == "content":
            theText = ""
            soup = BeautifulSoup(value, "html.parser")

            for h in soup.find_all('h1', 'h2', 'h3', 'b', 'title'):
                theText += h.string + " " + h.string + " " + h.string
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
    my_file = Path(r"C:\Users\hamza\OneDrive\Desktop\inverted-index-creator-main\inverted_index.txt")

    if my_file.is_file():
        with open("inverted_index.txt") as f:
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
    with open('inverted_index.txt', "w") as data:
        data.write(str(inverted_index))
    print(count)
    return length

def search(query,tot_count):
    max_tup=(0,0)
    tokens = query.split(' ')
    with open('inverted_index.txt', "r") as f:
        data = f.read()
    inverted_index = json.loads(data)
    f.close()
    for current_count in range(tot_count):
        temp=0
        for i in tokens:
            lis=inverted_index[i]
            temp+=lis[current_count]
        if temp> max_tup[0]:
            max_tup =(temp,current_count)
    file_json = open('json_files.txt', 'r')
    print(max_tup[0],file_json.readlines()[max_tup[1]])

def make_all_files_count():
    file_json = open('json_files.txt','w')
    for i in paths:
        file_json.write(i)
    file_json.close()

def main():
    # with open('inverted_index.txt', "r") as f:
    #     data = f.read()
    # inverted_index = json.loads(data)
    # f.close()
    # sort_ind = sorted(inverted_index)
    # with open("inverted_index.txt", 'w')as index:
    #     index.write(json.dumps(sort_ind))
    # f.close()
    # make_all_files_count()
    # start_time =time.time()
    # search(input('query: '),2839)
    # end_time = time.time()
    # print(end_time-start_time)
    count = 0
    length_of_unique = 0
    for folder in paths:
        corpus = generate_tokens(folder)
        length_of_unique = reportFunc(corpus,count)
        count += 1
    with open("report.txt", "w") as report:
        report.write("Number of Indexed Documents: " + str(count) + "\n")
        report.write("The number of unique word: " + str(length_of_unique) + "\n")
        #report.write("Size of Inverted Index: " + str(os.path.getsize(r"C:\Users\hamza\OneDrive\Desktop\inverted-index-creator-main\inverted_index.txt")) + "\n")

if __name__ == "__main__":
    main()