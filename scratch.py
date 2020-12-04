import os
import json
import time
import glob
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from pathlib import Path
from bs4 import BeautifulSoup
from multiprocessing import Pool
import math

paths = [file for file in glob.glob(r"C:\Users\hamza\OneDrive\Desktop\DEV\**\*json")]
my_file = Path(r"C:\Users\hamza\OneDrive\Desktop\inverted-index-creator-main\inverted_index.txt")
my_dup = Path(r"C:\Users\hamza\OneDrive\Desktop\inverted-index-creator-main\duplicate.txt")


def generate_tokens(file):
    f = open(file, "r")
    loader = json.load(f)
    for words, value in loader.items():
        if words == "content":
            theText = ""
            soup = BeautifulSoup(value, "html.parser")
            for h in soup.find_all('h1', 'h2', 'h3', 'b', 'title'):
                theText += h.string + " " + h.string + " " + h.string
            for h in soup.find_all('a'):
                theText += h.text
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
    ps = PorterStemmer()
    for s in sent_tokenize(text):
        token_words = word_tokenize(s.lower())
        temp = []
        for token in token_words:
            temp.append(ps.stem(token).strip(punc))
        corpus += temp
    if len(corpus) > 3000:
        return corpus[:3000]
    else:
        return corpus


def reportFunc(tokens, count, inverted_index, lines):
    file2 = open("file2.txt", "a+", encoding="utf-8")
    uniqe_words = list(lines)
    tokens = " ".join(tokens)
    in_file = False
    for token in range(len(''.join(tokens).split(" "))):
        temp = ''.join(tokens).split(" ")
        for line in lines:
            if temp[token] == line.strip("\n"):
                in_file = True
        if in_file is False and '-' != temp[token] and ',' not in temp[token] and '-' not in temp[token]:
            file2.write(temp[token] + "\n")
            uniqe_words.append(temp[token])
    file2.close()
    for unique in range(len(uniqe_words)):
        temp = uniqe_words[unique].strip('\n').strip(' ')
        if temp in inverted_index and tokens.count(temp) != 0:
            set_tup = inverted_index[temp]
            set_tup.add(str(tokens.count(temp)) + ":" + str(count) + ':'+str(int(len(tokens) / (tokens.index(temp) + 1))))
            inverted_index[temp] = set_tup
        elif tokens.count(temp) != 0:
            set_tup = {str(tokens.count(temp)) + ":" + str(count) + ':' + str(int(len(tokens) / (tokens.index(temp) + 1)))}
            inverted_index[temp] = set_tup
    return inverted_index


def search(start_time,short_index_list,relevant_files):
    max_tups = []
    stem_set_list=[]
    for i in short_index_list:
        stem_set_list.append(short_index_list[i])
    for current_count in relevant_files:
        started_file = False
        for i in stem_set_list: #takes sets from inverted index that are in inverted index casts as list now we iterate through those
            temp = [lis for lis in i if int(lis.split(':')[1])==int(current_count)] #gives u whatever tuples in i at file current_count
            if len(temp)!=0 and started_file==False:
                max_tups.append((math.log(int(temp[0].split(':')[0]))*int(temp[0].split(':')[2]),int(temp[0].split(':')[1])))
                started_file=True
            elif len(temp)!=0:
                max_tups[-1] = (int(max_tups[-1][0])+(math.log(int(temp[0].split(':')[0])))*int(temp[0].split(':')[2]),int(temp[0].split(':')[1]))
    end_time = time.time()
    print(end_time - start_time)

    file_json = open('json_files.txt', 'r', encoding ="utf-8")
    for i in sorted(max_tups, reverse=True)[:5]:
        file_json.seek(0)
        output = file_json.readlines()[i[1]]
        print(i[0], output.split("\\")[-1])
    file_json.close()


def make_all_files_count():
    file_json = open('json_files.txt', 'w', encoding="utf-8")
    for i in paths:
        file_json.write(i + "\n")
    file_json.close()


def find_duplicates(tot_files):
    with open('inverted_index.txt', "r", encoding="utf-8") as f:
        inverted_index = eval(f.read())
    stem_set_list = []
    for i in inverted_index:
        stem_set_list.append(list(inverted_index[i]))
    for prim_file in range(tot_files):
        for sec_file in range(tot_files):
            # similar files have at most 5% difference
            dup = True
            if prim_file != sec_file:
                for token in stem_set_list:
                    dict_prim = dict((v, k) for (k, v) in enumerate(int(tup.split(':')[1]) for tup in token))
                    try:
                        prim_tup = dict_prim[prim_file]
                    except:
                        prim_tup = 0
                    try:
                        sec_tup = dict_prim[sec_file]
                    except:
                        sec_tup = 0
                    if prim_tup != 0 and sec_tup != 0:
                        if prim_tup/sec_tup > 1.05 or prim_tup/sec_tup < .95:
                            dup = False
                    elif prim_tup == 0 and sec_tup > 5:
                        dup = False
                    elif sec_tup == 0 and prim_tup > 5:
                        dup = False
                if dup:
                    if my_dup.is_file():
                        dup_file = open('duplicate.txt', 'r+', encoding="utf-8")
                        duplicates = dup_file.readlines()
                    else:
                        dup_file = open('duplicate.txt', 'w', encoding="utf-8")
                        duplicates = []
                    dup_file.seek(0)
                    temp_lines = list(duplicates)
                    same_line = False
                    for line in range(len(temp_lines)):
                        if str(prim_file) in temp_lines[line].strip('\n').split(' ') and str(sec_file) not in temp_lines[line].strip('\n').split(' '):
                            duplicates[line] = duplicates[line].strip('\n') + " " + str(sec_file)
                        elif str(sec_file) in temp_lines[line].strip('\n').split(' ') and str(prim_file) not in temp_lines[line].strip('\n').split(' '):
                            duplicates[line] = duplicates[line].strip('\n') + " " + str(prim_file)
                        elif str(prim_file) in temp_lines[line].strip('\n').split(' ') and str(sec_file) in temp_lines[line].strip('\n').split(' '):
                            same_line = True
                    if temp_lines == duplicates and same_line is False:
                        duplicates.append(str(prim_file) + " " + str(sec_file))
                    for i in duplicates:
                        if i != '\n':
                            dup_file.write(i.strip('\n')+'\n')
                    dup_file.close()


def clear_duplicates():
    if my_dup.is_file():
        with open('inverted_index.txt', "r", encoding="utf-8") as f:
            inverted_index = eval(f.read())
        f.close()
        stem_set_list = []
        for i in inverted_index:
            stem_set_list.append(list(inverted_index[i]))
        dup_file = open('duplicate.txt', 'r+', encoding="utf-8")
        duplicates = dup_file.readlines()
        dup_file.close()
        for dup_series in duplicates:
            for dups in dup_series.split(' '):
                for token_lis in stem_set_list:
                    for i in range(len(token_lis)):
                        if int(token_lis[i].split(':')[1]) == dups:
                            token_lis.remove(token_lis[i])
        count = 0
        for i in inverted_index:
            inverted_index[i] = set(stem_set_list[count])
            count += 1
        dict_file = open('inverted_index.txt', "w", encoding="utf-8")
        dict_file.write(str(inverted_index))


def merge_indices(list_o_indices):
    result_dict = {}
    for i in list_o_indices:
        for toke in i:
            if toke in result_dict:
                result_dict[toke] = result_dict[toke] | i[toke]
            else:
                result_dict[toke] = i[toke]
    return result_dict


def mega_merge(ten_tho_counter):
    dict_1 = {}
    dict_2 = {}
    dict_3 = {}
    dict_4 = {}
    dict_5 = {}
    dict_6 = {}
    dict_7 = {}
    dict_8 = {}
    dict_9 = {}
    dict_10 = {}
    print('holy smokes')
    with open('inverted_index1.txt', "r", encoding="utf-8") as data:
        dict_1 = eval(data.read())
    with open('inverted_index2.txt', "r", encoding="utf-8") as data:
        dict_2 = eval(data.read())
    with open('inverted_index3.txt', "r", encoding="utf-8") as data:
        dict_3 = eval(data.read())
    with open('inverted_index4.txt', "r", encoding="utf-8") as data:
        dict_4 = eval(data.read())
    with open('inverted_index5.txt', "r", encoding="utf-8") as data:
        dict_5 = eval(data.read())
    with open('inverted_index6.txt', "r", encoding="utf-8") as data:
        dict_6 = eval(data.read())
    with open('inverted_index7.txt', "r", encoding="utf-8") as data:
        dict_7 = eval(data.read())
    with open('inverted_index8.txt', "r", encoding="utf-8") as data:
        dict_8 = eval(data.read())
    with open('inverted_index9.txt', "r", encoding="utf-8") as data:
        dict_9 = eval(data.read())
    with open('inverted_index1.txt', "r", encoding="utf-8") as data:
        dict_10 = eval(data.read())
    dict_1.update(dict_2)
    dict_1.update(dict_3)
    dict_1.update(dict_4)
    dict_1.update(dict_5)
    dict_1.update(dict_6)
    dict_1.update(dict_7)
    dict_1.update(dict_8)
    dict_1.update(dict_9)
    dict_1.update(dict_10)
    with open('inverted_index_first_' + str(ten_tho_counter) + '0.txt', "w", encoding="utf-8") as data:
        data.write(str(dict_1))
    print('we merged dat bih')


def run_load(tup_arg):
    folder = tup_arg[0]
    count = tup_arg[1]
    inverted_index = tup_arg[2]
    lines = tup_arg[3]
    corpus = generate_tokens(folder)
    print(count)
    return reportFunc(corpus, count, inverted_index, lines)


def main():
    run_type = input('r/s/c: ')
    if run_type =='s' and my_file.is_file():
        inverted_index = {}
        short_index={}
        with open('inverted_index.txt', "r", encoding ="utf-8") as f:
            inverted_index = eval(f.read())
        make_all_files_count()
        query = input('query: ')
        start_time = time.time()
        ps = PorterStemmer()
        tokens = query.split(' ')
        stems = []
        relevant_files= set()
        for token in tokens:
            stems.append(ps.stem(token))
        for stem in stems:
            try:
                if len(inverted_index[stem])<250:
                    short_index[stem]=inverted_index[stem]
                    for file in inverted_index[stem]:
                        relevant_files.add(int(file.split(':')[1]))
            except:
                pass
        if len(relevant_files) < 10:
            try:
                short_index[stem] = inverted_index[stem]
                for file in inverted_index[stem]:
                    relevant_files.add(file.split(':')[2])
            except:
                pass
        search(start_time,short_index,relevant_files)
    elif run_type=='r':
        inverted_index={}
        size_o_group=0
        group_index=[]
        for pat in range(len(paths)):
            pt=paths[pat]
            size_o_group+=os.path.getsize(pt)
            if size_o_group >= 100000:
                if len(group_index)>0:
                    group_index.append(pat-sum(group_index))
                else:
                    group_index.append(pat)
                size_o_group=0
        group_index.append(len(paths)-sum(group_index))
        num_of_paths=0
        status=0
        stopping_num=0 #if need to start run in middle
        temp_sum=0
        turnicate_group=0
        for i in range(len(group_index)):
            temp_sum+=group_index[i]
            if temp_sum>=stopping_num and turnicate_group==0:
                turnicate_group=i+1
        num_of_paths=sum(group_index[:turnicate_group])
        group_index = group_index[turnicate_group:]
        ten_tho_counter=0
        for i in range(len(group_index)):
            list_o_tups=[]
            start_time =time.time()
            file2 = open("file2.txt", "a+", encoding ="utf-8")
            lines= file2.readlines()
            file2.close()
            for j in range(group_index[i]):
                num_of_paths+=1
                list_o_tups.append((paths[num_of_paths],num_of_paths,inverted_index,lines))
            with Pool(int(group_index[i])) as p:
                list_o_indices = p.map(run_load,list_o_tups)
            list_o_indices.append(inverted_index)
            final_index=merge_indices(list_o_indices)
            if num_of_paths-10000*ten_tho_counter >1000 and status<1:
                with open('inverted_index1.txt', "w+", encoding ="utf-8") as data:
                    data.write(str(final_index))
                status=1
                final_index={}
            elif num_of_paths-10000*ten_tho_counter >2000 and status<2:
                with open('inverted_index2.txt', "w+", encoding ="utf-8") as data:
                    data.write(str(final_index))
                status=2
                final_index={}
            elif num_of_paths-10000*ten_tho_counter >3000 and status<3:
                with open('inverted_index3.txt', "w+", encoding ="utf-8") as data:
                    data.write(str(final_index))
                status=3
                final_index={}
            elif num_of_paths-10000*ten_tho_counter >4000 and status<4:
                with open('inverted_index4.txt', "w+", encoding ="utf-8") as data:
                    data.write(str(final_index))
                status=4
                final_index={}
            elif num_of_paths-10000*ten_tho_counter >5000 and status<5:
                with open('inverted_index5.txt', "w+", encoding ="utf-8") as data:
                    data.write(str(final_index))
                status=5
                final_index={}
            elif num_of_paths-10000*ten_tho_counter >6000 and status<6:
                with open('inverted_index6.txt', "w+", encoding ="utf-8") as data:
                    data.write(str(final_index))
                status=6
                final_index={}
            elif num_of_paths-10000*ten_tho_counter >7000 and status<7:
                with open('inverted_index7.txt', "w+", encoding ="utf-8") as data:
                    data.write(str(final_index))
                status=7
                final_index={}
            elif num_of_paths-10000*ten_tho_counter >8000 and status<8:
                with open('inverted_index8.txt', "w+", encoding ="utf-8") as data:
                    data.write(str(final_index))
                status=8
                final_index={}
            elif num_of_paths-10000*ten_tho_counter >9000 and status<9:
                with open('inverted_index9.txt', "w+", encoding ="utf-8") as data:
                    data.write(str(final_index))
                status=9
                final_index={}
            elif num_of_paths-10000*ten_tho_counter >10000 and status<10:
                with open('inverted_index10.txt', "w+", encoding ="utf-8") as data:
                    data.write(str(final_index))
                final_index={}
                ten_tho_counter+=1
                mega_merge(ten_tho_counter)
                status =0
                file = open("sample.txt", "r+")
                file.truncate(0)
                file.close()
            inverted_index=final_index
            end_time = time.time()
            print('indexed files '+str(num_of_paths-group_index[i])+' through '+str(num_of_paths)+' in '+str(end_time-start_time)+' seconds')
        with open('inverted_index'+str(status+1)+'.txt', "w+", encoding ="utf-8") as data:
            data.write(str(final_index))
        print(status+1)
        print('finished dat shit')
        dict_1={}
        dict_temp={}
        print('holy smokes')
        with open('inverted_index1.txt', "r", encoding ="utf-8") as data:
            dict_1=eval(data.read())
        for i in range(status):
            with open('inverted_index'+str(status+1)+'.txt', "r", encoding ="utf-8") as data:
                dict_temp = eval(data.read())
            dict_1.update(dict_temp)
        for i in range(5):
            with open('inverted_index_first_'+str(i+1)+'0.txt', "r", encoding ="utf-8") as data:
                dict_temp = eval(data.read())
            dict_1.update(dict_temp)
        with open('inverted_index.txt', "w", encoding ="utf-8") as data:
            data.write(str(dict_1))
        print('we merged dat bih')

    elif run_type == "c" and my_file.is_file():
        find_duplicates(55000)
        clear_duplicates(55000)
    elif run_type=='m':
        mega_merge()
    else:
        main()


if __name__ == "__main__":
    main()
