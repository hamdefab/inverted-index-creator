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
from multiprocessing import Pool

paths = [file for file in glob.glob(r"/Users/nicholasjaber/PycharmProjects/inf141/assignment 3/DEV/**/*json")]
my_file = Path(r"/Users/nicholasjaber/PycharmProjects/inf141/assignment 3/inverted_index.txt")
my_dup = Path(r"/Users/nicholasjaber/PycharmProjects/inf141/assignment 3/duplicate.txt")

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



def reportFunc(tokens,count,inverted_index,lines):
    file2 = open("file2.txt", "a+", encoding ="utf-8")
    uniqe_words = list(lines)
    tokens = " ".join(tokens)
    in_file = False
    for token in range(len(''.join(tokens).split(" "))):
        temp = ''.join(tokens).split(" ")
        for line in lines:
            if temp[token] == line.strip("\n"):
                in_file = True
        if in_file == False and '-' != temp[token] and ',' not in temp[token] and '-' not in temp[token]:
            file2.write(temp[token] + "\n")
            uniqe_words.append(temp[token])
    file2.close()
    for unique in range(len(uniqe_words)):
        temp = uniqe_words[unique].strip('\n').strip(' ')
        if temp in inverted_index and tokens.count(temp)!=0:
            set_tup= inverted_index[temp]
            set_tup.add(str(tokens.count(temp))+":"+str(count)+':'+str(int(len(tokens)/(tokens.index(temp)+1))))
            inverted_index[temp] = set_tup
        elif tokens.count(temp)!=0:
            set_tup={str(tokens.count(temp))+":"+str(count)+':'+str(int(len(tokens)/(tokens.index(temp)+1)))}
            inverted_index[temp] = set_tup
    #print(count)
    return inverted_index

def search(query,tot_count):
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
            temp = [lis for lis in i if int(lis.split(':')[1])==current_count] #gives u whatever tuples in i at file current_count
            if len(temp)!=0 and started_file==False:
                max_tups.append((int(temp[0].split(':')[0])*int(temp[0].split(':')[2]),int(temp[0].split(':')[1])))
                started_file=True
            elif len(temp)!=0:
                max_tups[-1] = (int(max_tups[-1][0])+int(temp[0].split(':')[0])*int(temp[0].split(':')[2]),int(temp[0].split(':')[1]))
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

def find_duplicates(tot_files):
    inverted_index={}
    with open('inverted_index.txt', "r", encoding ="utf-8") as f:
        inverted_index = eval(f.read())
    stem_set_list = []
    for i in inverted_index:
        stem_set_list.append(list(inverted_index[i]))
    for prim_file in range(tot_files):
        for sec_file in range(tot_files):
            #similar files have at most 5% difference
            dup=True
            if prim_file!=sec_file:
                for token in stem_set_list:
                    dict_prim = dict((v,k) for (k,v) in enumerate(int(tup.split(':')[1]) for tup in token))
                    try:
                        prim_tup = dict_prim[prim_file]
                    except:
                        prim_tup=0
                    try:
                        sec_tup = dict_prim[sec_file]
                    except:
                        sec_tup=0
                    if prim_tup !=0 and sec_tup !=0:
                        if prim_tup/sec_tup > 1.05 or prim_tup/sec_tup < .95:
                            dup=False
                    elif prim_tup ==0 and sec_tup>5:
                        dup = False
                    elif sec_tup ==0 and prim_tup>5:
                        dup = False
                if dup:
                    if my_dup.is_file():
                        dup_file = open('duplicate.txt','r+', encoding ="utf-8")
                        duplicates= dup_file.readlines()
                    else:
                        dup_file = open('duplicate.txt','w', encoding ="utf-8")
                        duplicates = []
                    dup_file.seek(0)
                    temp_lines = list(duplicates)
                    same_line=False
                    for line in range(len(temp_lines)):
                        if str(prim_file) in temp_lines[line].strip('\n').split(' ') and str(sec_file) not in temp_lines[line].strip('\n').split(' '):
                            duplicates[line] = duplicates[line].strip('\n')+" "+str(sec_file)
                        elif str(sec_file) in temp_lines[line].strip('\n').split(' ') and str(prim_file) not in temp_lines[line].strip('\n').split(' '):
                            duplicates[line] = duplicates[line].strip('\n')+" "+str(prim_file)
                        elif str(prim_file) in temp_lines[line].strip('\n').split(' ') and str(sec_file) in temp_lines[line].strip('\n').split(' '):
                            same_line=True
                    if temp_lines==duplicates and same_line ==False:
                        duplicates.append(str(prim_file)+" "+str(sec_file))
                    for i in duplicates:
                        if i!='\n':
                            dup_file.write(i.strip('\n')+'\n')
                    dup_file.close()

def clear_duplicates(tot_count):
    if my_dup.is_file():
        inverted_index={}
        with open('inverted_index.txt', "r", encoding ="utf-8") as f:
            inverted_index = eval(f.read())
        f.close()
        stem_set_list = []
        for i in inverted_index:
            stem_set_list.append(list(inverted_index[i]))
        dup_file = open('duplicate.txt','r+', encoding ="utf-8")
        duplicates= dup_file.readlines()
        dup_file.close()
        for dup_series in duplicates:
            valid_dup = dup_series.split(' ')[0]
            for dups in dup_series.split(' '):
                for token_lis in stem_set_list:
                    for i in range(len(token_lis)):
                        if int(token_lis[i].split(':')[1])==dups:
                            token_lis.remove(token_lis[i])
        count=0
        for i in inverted_index:
            inverted_index[i] = set(stem_set_list[count])
            count+=1
        dict_file=open('inverted_index.txt', "w", encoding ="utf-8")
        dict_file.write(str(inverted_index))

def merge_indicies(list_o_indicies):
    result_dict={}
    for i in list_o_indicies:
        for toke in i:
            if toke in result_dict:
                result_dict[toke]=result_dict[toke] | i[toke]
            else:
                result_dict[toke] = i[toke]
    return result_dict

def mega_merge():
    file2 = open("file2.txt", "a+", encoding ="utf-8")
    lines= file2.readlines()
    file2.close()
    for line in lines:
        with open('inverted_index.json', "rb", encoding ="utf-8") as data:
            json_obj = ijson.items(data,'item.drugs')
            set = (c for c in json_obj if c['type']==line.strip('\n'))
            print(set)



def run_load(tup_arg):
    folder=tup_arg[0]
    count=tup_arg[1]
    inverted_index=tup_arg[2]
    lines = tup_arg[3]
    corpus = generate_tokens(folder)
    return reportFunc(corpus,count,inverted_index,lines)


def main():
    run_type = input('r/s/c: ')
    if run_type =='s' and my_file.is_file():
        inverted_index = {}
        with open('inverted_index.txt', "r", encoding ="utf-8") as f:
            inverted_index = eval(f.read())
        make_all_files_count()
        start_time =time.time()
        search(input('query: '),2400)
        end_time = time.time()
        print(end_time-start_time)
    elif run_type=='r':
        inverted_index={}
        if my_file.is_file():
            with open("inverted_index.txt", encoding ="utf-8") as f:
                inverted_index = eval(f.read())
        for i in range(int(len(paths)/100)):
            list_o_tups=[]
            start_time =time.time()
            file2 = open("file2.txt", "a+", encoding ="utf-8")
            lines= file2.readlines()
            file2.close()
            for j in range(100):
                list_o_tups.append((paths[j+100*i],j+100*i,inverted_index,lines))
            with Pool(100) as p:
                list_o_indicies = p.map(run_load,list_o_tups)
            list_o_indicies.append(inverted_index)
            final_index=merge_indicies(list_o_indicies)
            #json_obj=json.dumps(final_index)
            with open('inverted_index.txt', "w", encoding ="utf-8") as data:
            #    data.seek(2)
            #    data.write(json_obj)
                data.write(str(final_index))
            inverted_index=final_index
            end_time = time.time()
            print('indexed files '+str(i*100)+' through '+str((i+1)*100)+' in '+str(end_time-start_time)+' seconds')

        print('finished dat shit')

    elif run_type == "c" and my_file.is_file():
        find_duplicates(2400)
        clear_duplicates(2400)
    else:
        main()


if __name__ == "__main__":
    main()