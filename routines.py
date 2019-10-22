from bs4 import BeautifulSoup
import re
import markdown
from urllib.parse import quote

def addMediaPointer(HTML, mediaDict):
    soup = BeautifulSoup(HTML, "html.parser")
    for mediaRelativePath, (mediaName, mediaType) in mediaDict.items():
        if mediaType == 'AUDIO':
            for item in soup.select('a[href="%s"]' % quote(mediaRelativePath)):
                audioSpan = soup.new_tag('span')
                audioSpan.string = '[sound:%s]' % mediaName
                item.replace_with(audioSpan)
        elif mediaType == 'IMAGE':
            for item in soup.select('img[src="%s"]' % quote(mediaRelativePath)):
                item['src'] = mediaName
        else:
            pass
    # f = open('/Users/tansongchen/Library/Application Support/Anki2/addons21/Evernote2Anki/test.txt', encoding='utf-8', mode = 'w')
    # f.write(str(soup) + str(mediaDict))
    # f.close()
    return str(soup)

def test():
    HTML = '<body><a href="test.source/test.wav">test.wav</a><img src="test.source/test.png"></body>'
    mediaDict = {'test.source/test.wav': ('newname.wav', 'AUDIO'), 'test.source/test.png': ('newname.png', 'IMAGE')}
    HTML = addMediaPointer(HTML, mediaDict)
    print(HTML)

def getQAFromHTML(HTML):
    QAList = []
    soup = BeautifulSoup(HTML, "html.parser")
    divl = soup.body.contents
    QField, AField = '', ''
    for div in divl:
        divs = div.get_text()
        if divs[:2] in ['q:', 'Q:', 'q：', 'Q：']:
            if (QField, AField) != ('', ''):
                QAList.append((QField, AField))
            QField = str(div)
            AField = ''
        elif divs[:2] in ['a:', 'A:', 'a：', 'A：']:
            AField = str(div)
        else:
            if AField == '':
                QField = QField + str(div)
            else:
                AField = AField + str(div)
    QAList.append((QField, AField))
    return QAList

def getTagsFromHTML(HTML):
	soup = BeautifulSoup(HTML, "html.parser")
	tagList = []
	for item in soup.select('head meta[name="keywords"]'):
		tagList += item['content'].split(', ')
	return tagList

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
    # extension_configs = {'extra': {}, 'tables': {}}
    heading = re.compile(r'^#{1,%s} ' % level, re.M)

    heading_match_iter = heading.finditer(md)
    block_list = []
    index = None
    for match in heading_match_iter:
        if index != None and md[index:index + level] == '#' * level:
            block_list.append(md[index:match.start()])
        index = match.start()
    block_list.append(md[index:])

    # f = open('logBlockList.txt', encoding='utf-8', mode = 'w')
    # for i in block_list:
    #     f.write(i)
    # f.close()

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
            AField += (math + AField_l[n+1])
        AField = enter.sub('', AField)
        # 回代代码
        AField_l = code_flag.split(AField)
        AField = AField_l[0]
        for n, code in enumerate(code_l):
            code = markdown.markdown(code)
            code = enter.sub('<br />', code)
            AField += (code + AField_l[n+1])
        QAList.append((QField, AField))
    return QAList

def getMetaFromMarkdowm(md):
	metaDict = {}
	mdRows = md.split('\n')
	if mdRows[0] != '---': return {}
	nRows = 1
	while ':' in mdRows[nRows]:
		key, value = mdRows[nRows].split(':', 1)
		metaDict[key.strip()] = value.strip()
		nRows += 1
	return metaDict
