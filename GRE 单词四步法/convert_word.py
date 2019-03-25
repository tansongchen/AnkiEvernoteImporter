# coding=utf-8
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
re_list_start = re.compile(r'^# \*\*List \d+', re.M)
re_strip_start = re.compile(r'# \*\*Word List 1(.|\n)*$')
re_unit_start = re.compile(r'^## \*\*Unit \d+', re.M)
re_word_start = re.compile(r'^\*\*(?P<word>[a-z \-éï]+)\*\*\n(?P<phon>\[.+\])?', re.U|re.M)
re_usage_start = re.compile(r'^\*\*【考(?:法|点)\d?】(.*)$', re.M|re.U)
re_phon = re.compile(r'\[.*\]', re.U)
re_pspeech = re.compile(r'\*([a-z\/\.]+)\*．')
re_escape_char = re.compile(r'\\(?=[\!\[\]()*+])')
re_fields_all = re.compile(r'^(\*\*[例近反派]\*\*)', re.M)
re_fields_der = re.compile(r'^(\*\*派\*\*)', re.M)
re_delimit = re.compile(r'\n|‖')
match_adj = re.compile(r'adj')
match_adv = re.compile(r'adv')

# 1 文件读取和初步处理
word_str = codecs_open_r_utf8('input/word.txt')
word_str = re_escape_char.sub('', word_str) # 先把转义用的\去掉
word_str = word_str.translate(dict.fromkeys((ord(c) for c in u"\xa0")))
word_str = collapse_blank_line(word_str) # 合并不必要的空行
# 2 把整个文件切成一个一个 List
word_lists_l = extract_content_between(word_str, re_list_start)
word_lists_l[30] = re_strip_start.sub('', word_lists_l[30])
# 3 把每个 List 切成一个一个 Unit
word_units_l_l = list(map(functools.partial(extract_content_between, match_re=re_unit_start), word_lists_l))

def UnitStr_to_WordDict_mono(unit_str, list_index, unit_index):
    returned_words_d_d = {}
    word_str_l = extract_content_between(unit_str, re_word_start)
    for word_str in word_str_l:
        first_line_match = re_word_start.match(word_str)
        try:
            word = first_line_match.group('word')
        except AttributeError:
            print(word_str)
        phon = first_line_match.group('phon')
        one_word_d = {'word_str': re_word_start.sub('', word_str), 
                      'phon': strF2H(phon) if phon else '', 
                      'pos': (list_index, unit_index),
                      'audio': ''} # Audio 备用
        returned_words_d_d[word] = one_word_d
    return returned_words_d_d

def UnitStr_to_WordDict(base_unit_data_l_l):
    _new3000_base_d = {}
    for list_index, unit_data_l in enumerate(base_unit_data_l_l):
        for unit_index, unit_data in enumerate(unit_data_l):
            _new3000_base_d.update(UnitStr_to_WordDict_mono(unit_data, list_index+1, unit_index+1))
    return _new3000_base_d

def WordStr_to_UsageList_mono(word_block_str, word, unit_index):

    usages_str_l = extract_content_between(word_block_str, re_usage_start)
    usages_d_l = []
    for one_usage_str in usages_str_l:
        fields_l = extract_content_between(one_usage_str[9:], re_fields_all, True)
        fields_l[-1] = ('\n'.join(fields_l[-1].split('\n')[:2]) + '\n') if unit_index == 10 else fields_l[-1]
        one_usage_str = ''.join(fields_l)
        origin_and_der = extract_content_between(one_usage_str, re_fields_der, True)
        # 1. Origin
        origin_field_list = extract_content_between(origin_and_der[0], re_fields_all, True)
        usage_d = FieldList_to_UsageDict(origin_field_list)
        # 2. Derivatives
        for one_der in origin_and_der[1:]:
            der_field_list = extract_content_between(one_der[6:], re_fields_all, True)
            usage_d['der'].append(FieldList_to_UsageDict(der_field_list))
        usages_d_l.append(usage_d)
    return usages_d_l

def FieldList_to_UsageDict(field_list):
    fields_c2e = {'例': 'examples', '近': 'syns', '反': 'ants'}
    usage_d = {'basic': [],
               'examples': [],
               'syns': [],
               'ants': [],
               'der': []}
    usage_d['basic'] = [BasicStr_to_BasicDict(basic_str.strip()) for basic_str in re_delimit.split(field_list[0].strip())]
    for i in field_list[1:]:
        usage_d[fields_c2e[i[2]]] = [x.strip() for x in re_delimit.split(i[6:].strip())]
    return usage_d

def BasicStr_to_BasicDict(basic_str):
    basic = {'exp': '', 
             'pspeech': '',
             'phon': '',
             'audio': '',
             'res': basic_str} # Audio 备用
    # 1.1 Phonetics
    phon_result = re_phon.search(basic_str)
    if phon_result:
        basic['phon'] = phon_result.group()
        basic_str = re_phon.sub('', basic_str, 1).strip()
    # 1.2 Part of Speech
    pspeech_result = re_pspeech.search(basic_str)
    if pspeech_result:
        pspeech = pspeech_result.group(1)
        pspeech = match_adj.sub('a', pspeech)
        pspeech = match_adv.sub('ad', pspeech)
        basic['pspeech'] = pspeech
        basic_str = re_pspeech.sub('', basic_str, 1)
    # 1.3 Explanation 就是剩下的！
    basic['exp'] = basic_str
    return basic
    
def WordStr_to_UsageList(words_d):
    for word in words_d:
        unit_index = word_d[word]['pos'][1]
        words_d[word]['usages'] = WordStr_to_UsageList_mono(words_d[word]['word_str'], word, unit_index)
        words_d[word].pop('word_str')
    return words_d

# 4 把每个 Unit 切成一个一个 Word
word_d = UnitStr_to_WordDict(word_units_l_l)
# 5 把每个 Word 切成一个一个 Usage，也就是考法。
word_d = WordStr_to_UsageList(word_d)
with codecs.open('input/word_json.txt', 'w', encoding='utf-8') as f:
    json.dump(word_d, f)
