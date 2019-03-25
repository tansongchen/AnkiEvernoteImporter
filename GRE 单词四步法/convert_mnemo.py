import re
import json
import codecs
import functools
import os.path
from random import random
from random import randint
from pprint import pprint
from copy import deepcopy
from my_helpers import *

# 0 正则表达式预备
re_escape_char = re.compile(r'\\(?=[\[\]()*+])') # 把转义符 \ 去掉
re_list_start = re.compile(r'### \*\*List \d+', re.M) # 每一个 List 的开头形如:### **List 1
re_root_start = re.compile(r'^\*\*\d+\.(.*)\*\*$\n|^Unit\d+$', re.M) # 每一个 root 的开头形如： **1.xxx**
re_word_start = re.compile(r'^\*\*([a-zéï-]+)(.*?)(\[.*\])\*\*$', re.M|re.I) # 每一个单词

# 1 读取文件并初步处理
mnemo_str = codecs_open_r_utf8('input/mnemo.txt')
mnemo_str = re_escape_char.sub('', mnemo_str) # 去掉 \
mnemo_str = collapse_blank_line(mnemo_str) # 合并不必要的空行
# 把文件拆成 List
mnemo_lists_l = extract_content_between(mnemo_str, re_list_start)

# 2 把 List 拆成 Root
def ListStr_to_RootDict(lists_l):
    root_d_l_l = []
    for list_index, list_str in enumerate(lists_l[:39]):
        root_d_l = []
        list_str = list_str.split('小结&复习')[0] # 一个 List 以小结复习结尾，这个我们用不到
        root_str_l = extract_content_between(list_str, re_root_start)
        for root_index, root_str in enumerate(root_str_l):
            root = re_root_start.search(root_str).group(1)
            # 只有在 List 1 到 34 且词根不是“其他xx”时才提取出词根，其余无效
            root = root.strip() if (list_index <= 33 and root[:2] != '其他') else ''
            root_str = root_str.split('【小结】')[0]
            root_str = re_root_start.sub('', root_str)
            root_d = {'pos': (list_index+1, root_index+1), 
                      'root': root,
                      'root_str': root_str} # 对每个 root 创建一个 dict
            root_d_l.append(root_d)
        root_d_l_l.append(root_d_l)
    return root_d_l_l

# 3 把 Root 拆成 Word
def RootDict_to_WordStr(root_d_l_l):
    path = [('all','',True),('all','',True),('key','root_str',False)]
    # 利用 path 进行复杂遍历的函数在 Helpers 中定义了
    for list_index, root_index, root_str in iter_through_general(root_d_l_l, path):
        root_d = root_d_l_l[list_index][root_index]
        word_str_l = extract_content_between(root_str, re_word_start, True)
        root_exp = word_str_l.pop(0).strip()
        root_d['root_exp'] = root_exp.split('\n')
        root_d['word_str_l'] = word_str_l
        root_d.pop('root_str')
    return root_d_l_l

# 4 把 Word 拆成三个部分
def WordStr_to_WordDict_mono(word_str): # 先定义单个的 word_str 怎么处理
    word_lines_l = [x.strip() for x in word_str.split('\n') if x.strip() != '']
    first_line_match = re_word_start.match(word_lines_l.pop(0))
    word = first_line_match.group(1)
    phon = first_line_match.group(3)
    word_d = {'word': word, 
              'phon': phon if phon else '',
              'content': word_lines_l}
    return word_d

def WordStr_to_WordDict(word_d_l_l):
    word_d = {}
    path = [('all','',True),('all','',True), ('key','word_str_l',False),('all','',True)]
    for list_index, root_index, word_index, word_str in iter_through_general(word_d_l_l, path):
        one_word_d = WordStr_to_WordDict_mono(word_str)
        word = one_word_d['word']
        for _key in ['pos', 'root', 'root_exp']: # 每个单词的 Dict 要继承自 root 的位置、词根和释义
            one_word_d[_key] = word_d_l_l[list_index][root_index][_key]
        one_word_d['cognates'] = ''
        word_d[word] = one_word_d
    return word_d

# 5 加同根词
def Add_Cognates(word_d, word_d_l_l):
    path = [('all','',False),('all','',False)]
    for root_d, in iter_through_general(word_d_l_l, path):
        root = root_d['root']
        root_exp = root_d['root_exp']
        if root != '' or root_exp != '': # 找到同一个词根下的所有词
            cognates_l = [re_word_start.match(x).group(1) for x in root_d['word_str_l']]
            for word in cognates_l:
                word_d[word]['cognates'] = ', '.join(cognates_l)
    return word_d

mnemo_root_l = ListStr_to_RootDict(mnemo_lists_l)
mnemo_word_s = RootDict_to_WordStr(mnemo_root_l)
mnemo_word_d = WordStr_to_WordDict(mnemo_word_s)
mnemo_word_d = Add_Cognates(mnemo_word_d, mnemo_word_s)
with codecs.open('input/mnemo_json.txt', 'w', encoding='utf-8') as f:
    json.dump(mnemo_word_d, f)
