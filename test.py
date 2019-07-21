from bs4 import BeautifulSoup

def getQA(HTML):
	QAList = []
	soup = BeautifulSoup(HTML, "html.parser")
	divl = soup.body.contents
	QField, AField = '', ''
	for div in divl:
		divs = div.get_text()
		if divs[:2] in ['q:', 'Q:', 'q：', 'Q：']:
			if (QField, AField) != ('', ''):
				QAList.append((QField, AField))
			QField = str(div)
			AField = ''
		elif divs[:2] in ['a:', 'A:', 'a：', 'A：']:
			AField = str(div)
		else:
			if AField == '':
				QField = QField + str(div)
			else:
				AField = AField + str(div)
	QAList.append((QField, AField))
	return QAList

f = open('印象笔记格式测试.html', encoding = 'utf-8', mode = 'r')
HTML = f.read()
f.close()

QAList = getQA(HTML)
for i in QAList:
	print(i)