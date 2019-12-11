from bs4 import BeautifulSoup
import markdown
import re
from routines import *

f = open('ceshi.md', encoding='utf-8', mode='r')
MD = f.read()
f.close()

# f = open('/Users/tansongchen/Desktop/我的笔记/印象笔记格式测试.html', encoding='utf-8', mode='r')
# HTML = f.read()
# f.close()

# mediaDict = getMediaFromFile('/Users/tansongchen/Desktop/我的笔记/印象笔记格式测试.html', [], ['jpg', 'png'])
# print(addMediaPointer(HTML, mediaDict))

# for QA in getQAFromHTML(HTML):
#     print(QA)
for QA in getQAFromMarkdown(MD, 2):
    print(QA)