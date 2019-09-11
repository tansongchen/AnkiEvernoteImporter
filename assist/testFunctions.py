from bs4 import BeautifulSoup

def getTags(HTML):
	soup = BeautifulSoup(HTML, "html.parser")
	tagList = []
	for item in soup.select('head meta[name="keywords"]'):
		tagList += item['content'].split(', ')
	return tagList

def getMetaFromMarkdowm(md):
	metaDict = {}
	mdRows = md.split('\n')
	if mdRows[0] != '---': return {}
	nRows = 1
	while ':' in mdRows[nRows]:
		key, value = mdRows[nRows].split(':', 1)
		metaDict[key.strip()] = value.strip()
		nRows += 1
	return metaDict

# f = open('/Users/tansongchen/Desktop/我的笔记/印象笔记格式测试.html', encoding = 'utf-8', mode = 'r')
# HTML = f.read()
# f.close()

# f = open('/Users/tansongchen/博客/source/_posts/elegant_pbs.md', encoding = 'utf-8', mode = 'r')
# MD = f.read()
# f.close()
