import re
import os
import markdown


def getQAFromMarkdown(md, level):
    QAList = []

    math_inline = re.compile(r'(?<![\\\$])\$(?!\$)(.+?)\$')
    math_block = re.compile(r'(?<!\\)\$\$(.+?)\$\$', re.S)
    math_all = re.compile(r'(?<![\\\$])\$(?!\$).+?\$|\n*(?<!\\)\$\$.+?\$\$\n*', re.S)
    code_block = re.compile(r'```.+?```', re.S)
    math_flag = re.compile(r'⚐')
    code_flag = re.compile(r'⚑')
    enter = re.compile(r'\n')
    lt = re.compile(r'\<')
    gt = re.compile(r'\>')
    amp = re.compile(r'\&')
    extension_configs = {
        'extra': {},
        'tables': {},
        'codehilite': {
            'linenums': True,
            'guess_lang': False
        }
    }
    heading = re.compile(r'^#{1,%s} ' % level, re.M)
    heading_match_iter = heading.finditer(md)
    block_list = []
    index = None
    for match in heading_match_iter:
        if index and md[index:index + level] == '#' * level:
            block_list.append(md[index:match.start()])
        index = match.start()
    block_list.append(md[index:])

    for block in block_list:
        QField, AField = block.split('\n', 1)
        QField = QField[level + 1:].strip()
        AField = AField.strip()
        code_l = code_block.findall(AField)
        AField = code_block.sub('⚑', AField)
        math_l = math_all.findall(AField)
        AField = math_inline.sub('⚐', AField)
        AField = math_block.sub('\n\n⚐\n\n', AField)
        AField = markdown.markdown(AField)
        # 回代数学
        AField_l = math_flag.split(AField)
        AField = AField_l[0]
        for n, math in enumerate(math_l):
            math = math_inline.sub('\\(\g<1>\\)', math)
            math = math_block.sub('\\[\g<1>\\]', math)
            math = amp.sub('&amp;', math)
            math = lt.sub('&lt;', math)
            math = gt.sub('&gt;', math)
            AField += (math + AField_l[n + 1])
        AField = enter.sub('', AField)
        # 回代代码
        AField_l = code_flag.split(AField)
        AField = AField_l[0]
        for n, code in enumerate(code_l):
            code = markdown.markdown(code,
                                     extensions=['markdown.extensions.fenced_code', 'markdown.extensions.codehilite'],
                                     extension_configs=extension_configs)
            code = enter.sub('<br />', code)
            AField += (code + AField_l[n + 1])
        print(AField)
        QAList.append((QField, AField))
    return QAList


def doImport():
    level = 2
    with open('ceshi.md', encoding='utf-8', mode='r') as f:
        source = f.read()
        QAList = getQAFromMarkdown(source, level)
        # print(QAList)


doImport()
