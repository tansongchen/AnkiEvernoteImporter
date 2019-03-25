import re
import os
import markdown

os.system("pbpaste > /Users/tansongchen/Public/Temp/paste.txt")
f = open('/Users/tansongchen/Public/Temp/paste.txt', encoding = 'utf-8', mode = 'r')
string = f.read()
f.close()

formula_inline = re.compile(r'(?<![\\\$])\$(?!\$)(.+?)\$')
formula_block = re.compile(r'(?<!\\)\$\$\n(.+?)\n\$\$', re.S)
formula_all = re.compile(r'(?<![\\\$])\$(?!\$).+?\$|(?<!\\)\$\$.+?\$\$', re.S)
flag = re.compile(r'⚐')
enter = re.compile(r'\n')
lt = re.compile(r'\<')
gt = re.compile(r'\>')
amp = re.compile(r'\&')

def process(section):
	section_title, section_body = section.split('\n\n', 1)
	section_title_l = section_title.split(' ', 1)
	note_l = section_body[3:].split('\n\n## ')
	section_output_l = []
	for note_number, note_content in enumerate(note_l):
		note_title, note_body = note_content.split('\n\n', 1)
		formula_l = formula_all.findall(note_body)
		note_body = formula_all.sub('⚐', note_body)
		note_body = markdown.markdown(note_body)
		note_body_l = flag.split(note_body)
		note_body = ''
		for n, formula in enumerate(formula_l):
			formula = formula_inline.sub('[$]\g<1>[/$]', formula)
			formula = formula_block.sub('[$$]\g<1>[/$$]', formula)
			formula = amp.sub('&amp;', formula)
			formula = lt.sub('&lt;', formula)
			formula = gt.sub('&gt;', formula)
			note_body += (note_body_l[n] + formula)
		note_body += note_body_l[-1]
		note_body = enter.sub('<none>', note_body)
		position = ['0%s%s%s%02d' % (metadata_l[0], metadata_l[2], section_title_l[0], note_number+1)]
		data_l = position + metadata_l + section_title_l + ['%02d' % (note_number+1), note_title, note_body]
		section_output_l.append(data_l)
	return section_output_l

metadata, content = string.split('\n\n', 1)
metadata_l = metadata.split(': ')[1].split('｜')
section_l = content[2:].split('\n\n# ')
note_l = sum(list(map(process, section_l)), [])
string = '\n'.join('\t'.join(x) for x in note_l)
f = open('/Users/tansongchen/Public/Temp/import.txt', encoding = 'utf-8', mode = 'w')
f.write(string)
f.close()