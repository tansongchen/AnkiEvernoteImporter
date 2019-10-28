import re
import os
import markdown

math_inline = re.compile(r'(?<![\\\$])\$(?!\$)(.+?)\$')
math_block = re.compile(r'(?<!\\)\$\$(.+?)\$\$', re.S)
math_all = re.compile(r'(?<![\\\$])\$(?!\$).+?\$|\n*(?<!\\)\$\$.+?\$\$\n*', re.S)
code_block = re.compile(r'```.+?```', re.S)
math_flag = re.compile(r'⚐')
code_flag = re.compile(r'⚑')
enter = re.compile(r'\n')
lt = re.compile(r'\<')
gt = re.compile(r'\>')
amp = re.compile(r'\&')
extension_configs = {
    # 'extra': {},
    # 'tables': {},
    # 'codehilite': {
    # 'linenums': True, 
    # 'guess_lang': False
    # }
}

def process(section):
	section_title, section_body = section.split('\n\n', 1)
	section_title_l = section_title.split(' ', 1)
	note_l = section_body[3:].split('\n\n## ')
	section_output_l = []
	for note_number, note_content in enumerate(note_l):
		note_title, note_body = note_content.split('\n\n', 1)
		code_l = code_block.findall(note_body)
		note_body = code_block.sub('⚑', note_body)
		math_l = math_all.findall(note_body)
		note_body = math_inline.sub('⚐', note_body)
		note_body = math_block.sub('\n\n⚐\n\n', note_body)
		note_body = markdown.markdown(note_body, extensions = extension_configs)
		# 回代数学
		note_body_l = math_flag.split(note_body)
		note_body = note_body_l[0]
		for n, math in enumerate(math_l):
			math = math_inline.sub('\\(\g<1>\\)', math)
			math = math_block.sub('\\[\g<1>\\]', math)
			math = amp.sub('&amp;', math)
			math = lt.sub('&lt;', math)
			math = gt.sub('&gt;', math)
			note_body += (math + note_body_l[n+1])
		note_body = enter.sub('', note_body)
		# 回代代码
		note_body_l = code_flag.split(note_body)
		note_body = note_body_l[0]
		for n, code in enumerate(code_l):
			code = markdown.markdown(code, extensions = extension_configs)
			code = enter.sub('<br />', code)
			note_body += (code + note_body_l[n+1])
		## 拼装
		if ( note_type == 'course' ):
			position = ['0%s%s%s%02d' % (metadata_l[0], metadata_l[2], section_title_l[0], note_number+1)]
			data_l = position + metadata_l + section_title_l + ['%02d' % (note_number+1), note_title, note_body]
		else:
			data_l = [note_title, note_body]
		section_output_l.append(data_l)
	return section_output_l

note_type = 'basic'
# note_type = 'course'
os.system("pbpaste > /Users/tansongchen/Public/Temp/paste.txt")
f = open('/Users/tansongchen/Public/Temp/paste.txt', encoding = 'utf-8', mode = 'r')
string = f.read()
f.close()

if ( note_type == 'course' ):
	metadata, content = string.split('\n\n', 1)
	metadata_l = metadata.split(': ')[1].split('｜')
else:
	content = string
section_l = content[2:].split('\n\n# ')
note_l = sum(list(map(process, section_l)), [])
string = '\n'.join('\t'.join(x) for x in note_l)
f = open('/Users/tansongchen/Public/Temp/import.txt', encoding = 'utf-8', mode = 'w')
f.write(string)
f.close()