from bs4 import BeautifulSoup
import markdown
import re
from routines import *

f = open('example.md', encoding='utf-8', mode='r')
MD = f.read()
f.close()

f = open('example.html', encoding='utf-8', mode='r')
HTML = f.read()
f.close()

for QA in getQAFromHTML(HTML):
    print(QA)
# getQAFromMarkdown(HTML, 2)