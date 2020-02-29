from bs4 import BeautifulSoup
import markdown
import re
from routines import *

# f = open('ceshi.md', encoding='utf-8', mode='r')
# MD = f.read()
# f.close()
# for QA in getQAFromMarkdown(MD, 2):
#     print(QA)

f = open('/Users/tansongchen/Desktop/Q.A/YinXiangBiJi.enex.html', encoding='utf-8', mode='r')
HTML = f.read()
f.close()

for QA in getQAFromHTML(HTML):
    print(QA)