'''
运行测试
'''

from bs4 import BeautifulSoup
from .preprocessor import preprocess
from .qa import split

with open('test/test.md') as f:
    md = f.read()
    html = preprocess(md)
    soup = BeautifulSoup(html, 'html.parser')
    for qa in split(soup, 2):
        print(qa)

with open('/Users/tansongchen/Desktop/我的笔记2/测试.html') as f:
    html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    for qa in split(soup, 2):
        print(qa)
