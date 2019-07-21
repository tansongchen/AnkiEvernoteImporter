# coding=utf-8
# 把原文件中的问题解决

f = open('word_raw.txt', encoding = 'utf-8', mode = 'r')
l = f.readlines()[:75263]
f.close()

def a(line, char, space=0):
    global l
    l[line] = l[line][:char] + ' ‖ ' + l[line][char+space:]

# 修正：无分隔符或分隔符错误
a(2180,114,1)
a(7619,80)
a(9387,21,1)
a(53326,81)
a(67087,76)
a(68349,69,1)
a(70541,126,1)
a(71683,78)

# 修正：领域错误
l[3017] = '**近**\n'
l[37948] = '**近**\n'
l[45042] = '**例**\n'
l[48901] = '**近**\n'
l[56230] = '**近**\n'
l[56234] = '**反**\n'
l[57000] = '**例**\n'
l[68839] = '**派**\n'

# 修正：无音标
l[3139] = '\[ˈænɪmət\] ' + l[3139]
l[10379] = '\[ˈkɑːmplɪmənt\]\n'
l[10531] = '\[kəmˈpaʊnd\] ' + l[10531]
l[12041] = '\[kənˈtrækt\] ' + l[12041]

# 其他
l[1154] = '*v*．**不正当或不合理使用、过分过量使用：**to put to a **wrong or improper use** or to **use excessively**\n'
l[14070] = 'undaunted *adj*．无畏的，大胆的\n'
l[14872] = l[14872].strip('\n') + ', ' + l[14876]
l[14874] = '\n'
l[14876] = '\n'
l[16593] = l[16593][:57]
l[16613] = 'disarm her anger　平息她的怒气\n'
l[20486] = l[20486][:44] + ',' + l[20486][45:]
l[28648] = 'humbuggery　欺骗\n'
l[68563] = l[68563][:77] + l[68563][78:81] + ' ‖ ' + l[68563][81:]
l[73646] = '[ˈprodʒekt]\n'

f = open('word.txt', encoding = 'utf-8', mode = 'w')
f.write(''.join(l))
f.close()
