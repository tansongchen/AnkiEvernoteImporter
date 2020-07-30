'''
运行测试
'''

from bs4 import BeautifulSoup
from src.preprocessor import preprocess
from src.qa import split, splitLegacy

with open('test/test.md') as f:
    md = f.read()
    html = preprocess(md)
    soup = BeautifulSoup(html, 'html.parser')
    for qa in split(soup, 2):
        print(qa)

with open('test/test.html') as f:
    html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    for qa in split(soup, 2):
        print(qa)

with open('test/test.legacy.html') as f:
    html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    for qa in splitLegacy(soup):
        print(qa)
