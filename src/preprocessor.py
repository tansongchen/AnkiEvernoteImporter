'''
将普通笔记和 Markdown 笔记预处理为超级笔记的预处理器
'''

import sys
import pathlib
import importlib.util

addon_root = pathlib.Path(__file__).resolve().parent
pygments_source = addon_root / 'pygments' / '__init__.py'
spec = importlib.util.spec_from_file_location('pygments', pygments_source)
module = importlib.util.module_from_spec(spec)
sys.modules['pygments'] = module
spec.loader.exec_module(module)

import re
from hashlib import md5
from markdown import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.codehilite import CodeHiliteExtension

def preprocess(text):
    '''
    将 Markdown 文本预处理为 HTML
    '''

    md = text
    inlineMathRegex = re.compile(r'(?<![\\\$])\$(?!\$)(.+?)\$')
    blockMathRegex = re.compile(r'(?<!\\)\$\$(.+?)\$\$', re.S)
    inline = {}
    block = {}

    for inlineMath in inlineMathRegex.findall(md):
        placeholder = md5(inlineMath.encode('utf-8')).hexdigest()
        md = inlineMathRegex.sub(placeholder, md, 1)
        inline[placeholder] = inlineMath
    for blockMath in blockMathRegex.findall(md):
        placeholder = md5(blockMath.encode('utf-8')).hexdigest()
        md = blockMathRegex.sub(placeholder, md, 1)
        block[placeholder] = blockMath

    html = markdown(md, tab_length=2, extensions=[TableExtension(), FencedCodeExtension(), CodeHiliteExtension()])

    for inlineHash, inlineMath in inline.items():
        html = html.replace(inlineHash, '\\(%s\\)' % inlineMath)
    for blockHash, blockMath in block.items():
        html = html.replace(blockHash, '\\[%s\\]' % blockMath)

    return '<html><body>%s</body></html>' % html
