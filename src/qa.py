'''
从超级笔记中提取 QA
'''

from urllib.parse import quote

class QA:
    def __init__(self, qTag):
        self.question = str(qTag)
        self.answer = ''

    def append(self, aTag):
        self.answer += str(aTag)

    def __repr__(self):
        return 'Q: %s\nA:%s\n' % (self.question, self.answer)

    def __str__(self):
        return 'Q: %s\nA:%s\n' % (self.question, self.answer)

def split(soup, level):
    qaList = []
    qName = 'h%d' % level
    parentNames = ['h%d' for i in range(1, level)]
    buffer = False
    for child in soup.body.children:
        if child.name in parentNames:
            buffer = False
        elif child.name == qName:
            buffer = True
            qaList.append(QA(child))
        else:
            if buffer: qaList[-1].append(child)
    return qaList

def splitLegacy(soup):
    '''
    按照定界符的规则划分笔记
    '''
    QAList = []
    meta = soup.select_one('head meta[name="exporter-version"]')
    if meta and 'Mac' in meta['content']:
        blockList = soup.select('body > *')
    else:
        blockList = soup.select('body > div > span > div > *')
    QField, AField = '', ''
    for block in blockList:
        string = block.get_text().strip()
        if string[:2] in ['q:', 'Q:', 'q：', 'Q：']:
            if (QField, AField) != ('', ''):
                QAList.append((QField, AField))
            QField = str(block)
            AField = ''
        elif string[:2] in ['a:', 'A:', 'a：', 'A：']:
            AField = str(block)
        else:
            if AField:
                AField = AField + str(block)
            elif QField:
                QField = QField + str(block)
    QAList.append((QField, AField))
    return QAList

def updateMedia(soup, audioDict, picsDict):
    for mediaRelativePath, mediaName in audioDict.items():
        for item in soup.select('a[href="%s"]' % quote(mediaRelativePath)):
            audioSpan = soup.new_tag('span')
            audioSpan.string = '[sound:%s]' % mediaName
            item.replace_with(audioSpan)
    for mediaRelativePath, mediaName in picsDict.items():
        for item in soup.select('img[src="%s"]' % quote(mediaRelativePath)):
            item['src'] = mediaName
    return soup
