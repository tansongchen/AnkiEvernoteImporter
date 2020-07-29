'''
将普通笔记和 Markdown 笔记预处理为超级笔记的预处理器
'''

import re
from hashlib import md5
from markdown import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension

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

    html = markdown(md, tab_length=2, extensions=[TableExtension(), FencedCodeExtension()])

    for inlineHash, inlineMath in inline.items():
        html = html.replace(inlineHash, '\\(%s\\)' % inlineMath)
    for blockHash, blockMath in block.items():
        html = html.replace(blockHash, '\\[%s\\]' % blockMath)

    return '<html><body>%s</body></html>' % html
