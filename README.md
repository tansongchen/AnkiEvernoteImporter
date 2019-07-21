# Evernote2Anki

与小能熊终身学习学院「知识内化训练营」配套的笔记自动化导入插件。源代码由两个文件组成：

1. `__init__.py`：展示导入界面，操作数据库
2. `dialog.ui`：导入界面的具体配置

而 `dialog.py` 是用 `PyQt` 自动生成的界面程序。编译命令为：

```bash
pyuic5 -o dialog.py dialog.ui
```

`/old/` 中存放了以前的一些自动化的尝试，供参考。

`/bs4/` 是本插件解析 HTML 所依赖的 Beautiful Soup 库。未来可能会添加解析 Markdown 的库。

# 开发进度

## 2019 年 7 月 21 日｜version 0.1

基于「Media Import」插件修改，目前已经实现：

### 导入对话框编写

![](http://img.candobear.com/2019-07-21-133414.png)

- 选择（由印象笔记导出的）HTML 文件；
- 选择导入卡组；
- 选择笔记类型；
- 将 Q 字段和 A 字段对应到正面和背面。

### 基本实现 HTML 解析功能

用 Beautiful Soup 4 库解析，其中关键算法为：

```python
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
```

该算法的鲁棒性正在进行测试，可能有更好的算法。

# 预告

- Markdown 解析功能
- 导入时如有第一字段相同，覆盖/不变/重复的选项
- 与印象笔记 API 连接
- ……

