import re
import os
import markdown

os.system("pbpaste > /Users/tansongchen/Public/Temp/paste.txt")
f = open('/Users/tansongchen/Public/Temp/paste.txt', encoding = 'utf-8', mode = 'r')
string = f.read()
f.close()

extension_configs = {
    'extra': {},
    'tables': {},
    'codehilite': {
    'linenums': True,
    'guess_lang': False
    }
}

formula_inline = re.compile(r'(?<![\\\$])\$(?!\$)(.+?)\$')
formula_block = re.compile(r'(?<!\\)\$\$\n(.+?)\n\$\$', re.S)
formula_all = re.compile(r'(?<![\\\$])\$(?!\$).+?\$|(?<!\\)\$\$.+?\$\$', re.S)
flag1 = re.compile(r'⚐')
flag2 = re.compile(r'⚑')
enter = re.compile(r'\n')
lt = re.compile(r'\<')
gt = re.compile(r'\>')
amp = re.compile(r'\&')
code_block_pre = re.compile(r'```fortran(.+?)```', re.S)
code_block_post = re.compile(r'(\<div class.+?\<\/div\>)', re.S)

def process(section):
	section_title, section_body = section.split('\n\n', 1)
	section_title_l = section_title.split(' ', 1)
	note_l = section_body[3:].split('\n\n## ')
	section_output_l = []
	for note_number, note_content in enumerate(note_l):
		note_title, note_body = note_content.split('\n\n', 1)
		formula_l = formula_all.findall(note_body)
		note_body = formula_all.sub('⚐', note_body)
		note_body = markdown.markdown(note_body, extensions = extension_configs)
		code_l = code_block_post.findall(note_body)
		note_body = code_block_post.sub('⚑', note_body)
		for n, formula in enumerate(formula_l):
			formula = formula_inline.sub('[$]\g<1>[/$]', formula)
			formula = formula_block.sub('[$$]\g<1>[/$$]', formula)
			formula = amp.sub('&amp;', formula)
			formula = lt.sub('&lt;', formula)
			formula = gt.sub('&gt;', formula)
			note_body = flag1.sub(formula, note_body, 1)
		for n, code in enumerate(code_l):
			code = enter.sub('<br />', code)
			note_body = flag2.sub(code, note_body, 1)
		note_body = enter.sub('<none>', note_body)
		data_l = [note_title, note_body]
		section_output_l.append(data_l)
	return section_output_l

string = code_block_pre.sub('```\n:::fortran\g<1>```', string)
section_l = string[2:].split('\n\n# ')
note_l = sum(list(map(process, section_l)), [])
string = '\n'.join('\t'.join(x) for x in note_l)
f = open('/Users/tansongchen/Public/Temp/import.txt', encoding = 'utf-8', mode = 'w')
f.write(string)
f.close()