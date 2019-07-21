# coding=utf-8
import json
import codecs
import os
from my_helpers import *
import gzip
import shutil
from pydub import AudioSegment
import glob


# 0 正则表达式预备
re_us_pron = re.compile('\[s\](us.*?)\[/s\]')
re_pspeech = re.compile('^[ \t]*?\[m1\]\[b\].*?\[/b\] \[i\] ([a-z, ]+).*?\[/i\]', re.M)
re_word = re.compile(r'^([a-z-]+)[ \t]*$(.*?)(?=^[^ \t])', re.M|re.S|re.I)

# 1 文件读取和初步处理
output = 'output'
source = 'input/pron'
word_d = is_file_and_json_load('input/word_json.txt')
mnemo_d = is_file_and_json_load('input/mnemo_json.txt')
multi_pron = [word for word in word_d
                   if any(basic['phon'] for usage in word_d[word]['usages']
                                        for basic in usage['basic'])]
# 词典数据文件
dsl_pron_d = {}
dsl_str = gzip.open('input/pron.dsl.dz', mode='r').read().decode('utf-16')
for one_match_obj in re_word.finditer(dsl_str):
    word = one_match_obj.group(1)
    word_block = one_match_obj.group(2)
    dsl_pron_d[word] = {'word_block': word_block,
                        'pspeech_l': re_pspeech.findall(word_block),
                        'phon_l': re_us_pron.findall(word_block)}

# 2 加入发音指针
def add_audio_pointer(word):
    one_word_d = word_d[word]
    word = word.replace('é', 'e').replace('ï', 'i').split('/')[0]
    source_file_name = None
    if word not in dsl_pron_d:
        return
    dsl_word_d = dsl_pron_d[word]
    if word not in multi_pron:
        source_file_name = source + '/' + dsl_word_d['phon_l'][0]
        output_file_name = output + '/' + word + '.wav'
        one_word_d['audio'] = '[sound:' + word + '.mp3]'
        if not os.path.isfile(output_file_name) and os.path.isfile(source_file_name):
            shutil.copy(source_file_name, output_file_name)
    else:
        for usage_d in one_word_d['usages']:
            for basic_d in usage_d['basic']:
                book_pspeech = basic_d['pspeech']
                if book_pspeech in ['vt', 'vi']:
                    book_pspeech = 'v'
                for index, dsl_pspeech in enumerate(dsl_word_d['pspeech_l']):
                    for dsl_sub_pspeech in dsl_pspeech.split(','):
                        if dsl_sub_pspeech.strip().startswith(book_pspeech):
                            source_file_name = source + '/' + dsl_word_d['phon_l'][index]
                            break
                if source_file_name:
                    output_file_name = output + '/' + word + '_' + book_pspeech + '.wav'
                    basic_d['audio'] = '[sound:' + word + '_' + book_pspeech + '.mp3]'
                    if not os.path.isfile(output_file_name) and os.path.isfile(source_file_name):
                        shutil.copy(source_file_name, output_file_name)

for word in word_d:
    add_audio_pointer(word)

# 3. 将 wav 转换为 mp3，因为只有 mp3 能在手机上发音
def convert_to_mp3():
    owd = os.getcwd()
    os.chdir(output)
    for audio in glob.glob('*.wav'):
        mp3_filename = os.path.splitext(os.path.basename(audio))[0] + '.mp3'
        if not os.path.isfile(mp3_filename):
            AudioSegment.from_file(audio).export(mp3_filename, format='mp3')
    os.chdir(owd)

convert_to_mp3()

# 4. 把word和mnemo的字典转化为可以导入的note
def Dict_to_Note():
    output_list = []
    join2 = '<br />　　'.join
    join3 = '<br />　　　'.join
    join4 = '<br />　　　　'.join
    for word in word_d:
        # 1. 单词部分
        one_word_d = word_d[word]
        pos_L, pos_U = one_word_d['pos']
        pos = 'L' + ('0' + str(pos_L))[-2:] + ' U' + ('0' + str(pos_U))[-2:]
        pronon = one_word_d['phon'] + one_word_d['audio'] + ('<br />' if one_word_d['phon'] else '')
        
        # 2. 助记部分
        etym = ''
        if word in mnemo_d:
            mnemo = mnemo_d[word]
            compos = '<hr />__构词__　%s<br />' % join3(mnemo['content']) if mnemo['content'] else ''
            root = '__词根__　__%s__　%s<br />' % (mnemo['root'], join3(mnemo['root_exp'])) if mnemo['root'] else ''
            cognates = '__同根__　%s<br />' % mnemo_d[word]['cognates'] if mnemo['root'] else ''
            etym = compos + root + cognates

        # 3. 考法部分
        exam = ''
        for usage_index, usage in enumerate(one_word_d['usages']):
            origin = '<hr />【__考法 %d__】<br />' % (usage_index+1)
            der = ''
            for one_basic in usage['basic']:
                one_pron_str = '%s %s<br />' % (one_basic['phon'], one_basic['audio']) if one_basic['phon'] else ''
                one_exp_str = '%s. %s<br />' % (one_basic['pspeech'], one_basic['exp'])
                origin += (one_pron_str + one_exp_str)
            origin += '__例__　%s<br />' % join2(usage['examples']) if usage['examples'] else ''
            origin += '__近__　%s<br />' % join2(usage['syns']) if usage['syns'] else ''
            origin += '__反__　%s<br />' % join2(usage['ants']) if usage['ants'] else ''
            for der_d in usage['der']:
                der += '__派__　%s. %s<br />' % der_d['basic'][0]['pspeech'], der_d['basic'][0]['exp'] if der_d['basic'] else ''
                der += '　　__例__　%s<br />' % join4(der_d['examples']) if der_d['examples'] else ''
                der += '　　__近__　%s<br />' % join4(der_d['syns']) if der_d['syns'] else ''
                der += '　　__反__　%s<br />' % join4(der_d['ants']) if der_d['ants'] else ''
            exam += (origin + der)

        one_line = [word, pos, pronon, '', etym, exam]
        one_line = [custom_html_element(x).replace('\n', '～') for x in one_line]
        output_list.append(one_line)
    return output_list

import_data = sorted(Dict_to_Note(), key=lambda x: x[1]+x[0])
with codecs.open('output/anki_import.txt', 'w', encoding='utf-8') as f:
    for one_line in import_data:
        one_string = '\t'.join(one_line) + '\n'
        f.write(one_string)
