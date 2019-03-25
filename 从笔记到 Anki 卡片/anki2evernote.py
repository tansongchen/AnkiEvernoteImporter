import re
import tomd
import subprocess

f = open('/Users/tansongchen/Public/Temp/export.txt', encoding = 'utf-8', mode = 'r')
note_l = sorted([line.split('\t') for line in f], key = lambda x:x[0])
f.close()

formula_inline = re.compile(r'\[\$\](.+?)\[\/\$\]')
formula_block = re.compile(r'\[\$\$\](.+?)\[\/\$\$\]')
line_break = re.compile(r'\<none\>')
lt = re.compile(r'\&lt;')
gt = re.compile(r'\&gt;')
amp = re.compile(r'\&amp;')

def process(section_s):
	output_s = '# %s\n\n' % section_s
	note_s_l = []
	for i in section_d[section_s]:
		note_title = '## %s\n' % i[0]
		note_body = line_break.sub('\n', i[1])
		note_body = tomd.Tomd(note_body).markdown
		note_body = formula_inline.sub('$\g<1>$', note_body)
		note_body = formula_block.sub('$$\n\g<1>\n$$', note_body)
		note_body = lt.sub('<', note_body)
		note_body = gt.sub('>', note_body)
		note_body = amp.sub('&', note_body)
		note_body += '\n'
		note_s = note_title + note_body
		output_s += note_s
	return output_s

example = note_l[0]
metadata = '[comment]: %s\n\n' % '｜'.join(example[1:5])
section_d = {'%s %s' % (x[5], x[6]): [] for x in note_l}
for i in note_l:
	section_s = '%s %s' % (i[5], i[6])
	section_d[section_s].append((i[8], i[9]))
section_s_l = list(map(process, sorted(section_d.keys())))
string = metadata + ''.join(section_s_l)

p1 = subprocess.Popen(["echo", string], stdout=subprocess.PIPE)
subprocess.Popen(["pbcopy"], stdin=p1.stdout)