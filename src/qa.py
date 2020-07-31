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
    
    def appendLegacy(self, tag, to):
        if to == 'q':
            self.question += str(tag)
        else:
            self.answer += str(tag)

    def __repr__(self):
        return 'Q: %s\nA: %s\n' % (self.question, self.answer)

def split(soup, level):
    qaList = []
    qName = 'h%d' % level
    parentNames = ['h%d' for i in range(1, level)]
    buffer = False
    for child in soup.body.find_all(recursive=False):
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
    qaList = []
    meta = soup.select_one('head meta[name="exporter-version"]')
    if meta and 'Mac' in meta['content']:
        children = soup.body.find_all(recursive=False)
    elif meta and 'Windows' in meta['content']:
        children = soup.body.div.span.find_all(recursive=False)
    else:
        raise ValueError('不能识别笔记的来源')
    to = 'q'
    for child in children:
        string = child.get_text().strip()
        if string[:2] in ['q:', 'Q:', 'q：', 'Q：']:
            qaList.append(QA(child))
            to = 'q'
        elif string[:2] in ['a:', 'A:', 'a：', 'A：']:
            to = 'a'
            qaList[-1].appendLegacy(child, to)
        else:
            if qaList: qaList[-1].appendLegacy(child, to)
    return qaList

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
