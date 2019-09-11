from aqt import mw
from aqt.qt import *
from aqt.deckchooser import DeckChooser
from aqt import editor
from anki import notes
from . import dialog
from bs4 import BeautifulSoup
import re
import os
import markdown
from urllib.parse import quote

# Possible field mappings
ACTIONS = ['', '问题', '答案']
AUDIO = editor.audio
IMAGE = editor.pics
SPECIAL_FIELDS = ['Tags']

def addMediaPointer(HTML, mediaDict):
    soup = BeautifulSoup(HTML, "html.parser")
    for mediaRelativePath, (mediaName, mediaType) in mediaDict.items():
        if mediaType == 'AUDIO':
            for item in soup.select('a[href="%s"]' % quote(mediaRelativePath)):
                audioSpan = soup.new_tag('span')
                audioSpan.string = '[sound:%s]' % mediaName
                item.replace_with(audioSpan)
        elif mediaType == 'IMAGE':
            for item in soup.select('img[src="%s"]' % quote(mediaRelativePath)):
                item['src'] = mediaName
        else:
            pass
    # f = open('/Users/tansongchen/Library/Application Support/Anki2/addons21/Evernote2Anki/test.txt', encoding='utf-8', mode = 'w')
    # f.write(str(soup) + str(mediaDict))
    # f.close()
    return str(soup)

def test():
    HTML = '<body><a href="test.source/test.wav">test.wav</a><img src="test.source/test.png"></body>'
    mediaDict = {'test.source/test.wav': ('newname.wav', 'AUDIO'), 'test.source/test.png': ('newname.png', 'IMAGE')}
    HTML = addMediaPointer(HTML, mediaDict)
    print(HTML)

def getQAFromHTML(HTML):
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

def getTagsFromHTML(HTML):
	soup = BeautifulSoup(HTML, "html.parser")
	tagList = []
	for item in soup.select('head meta[name="keywords"]'):
		tagList += item['content'].split(', ')
	return tagList

def getQAFromMarkdown(md, level):
    QAList = []

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
    # extension_configs = {'extra': {}, 'tables': {}}
    heading = re.compile(r'^#{1,%s} ' % level, re.M)

    heading_match_iter = heading.finditer(md)
    block_list = []
    index = None
    for match in heading_match_iter:
        if index and md[index:index + level] == '#' * level:
            block_list.append(md[index:match.start()])
        index = match.start()
    block_list.append(md[index:])

    # f = open('logBlockList.txt', encoding='utf-8', mode = 'w')
    # for i in block_list:
    #     f.write(i)
    # f.close()

    for block in block_list:
        QField, AField = block.split('\n', 1)
        QField = QField[level + 1:].strip()
        AField = AField.strip()
        code_l = code_block.findall(AField)
        AField = code_block.sub('⚑', AField)
        math_l = math_all.findall(AField)
        AField = math_inline.sub('⚐', AField)
        AField = math_block.sub('\n\n⚐\n\n', AField)
        AField = markdown.markdown(AField)
        # 回代数学
        AField_l = math_flag.split(AField)
        AField = AField_l[0]
        for n, math in enumerate(math_l):
            math = math_inline.sub('\\(\g<1>\\)', math)
            math = math_block.sub('\\[\g<1>\\]', math)
            math = amp.sub('&amp;', math)
            math = lt.sub('&lt;', math)
            math = gt.sub('&gt;', math)
            AField += (math + AField_l[n+1])
        AField = enter.sub('', AField)
        # 回代代码
        AField_l = code_flag.split(AField)
        AField = AField_l[0]
        for n, code in enumerate(code_l):
            code = markdown.markdown(code)
            code = enter.sub('<br />', code)
            AField += (code + AField_l[n+1])
        QAList.append((QField, AField))
    return QAList

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

def doImport():
    # Raise the main dialog for the add-on and retrieve its result when closed.
    level = 2
    (file, did, model, fieldList, ok) = ImportSettingsDialog().getDialogResult()
    if not ok: return
    if os.path.splitext(file)[-1] == '.html':
        ACTIONS = ACTIONS + ['标签']
        f = open(file, encoding = 'utf-8', mode = 'r')
        source = f.read()
        f.close()
        mediaDir = os.path.splitext(file)[0] + '.resources'
        # 检查同目录下是否有 Evernote 自动生成的 .resources 目录，如果有则导入媒体文件，如果没有则不导入
        if os.path.exists(mediaDir):
            mediaList = os.listdir(mediaDir)
        else:
            mediaList = []
        mediaDict = {}
        for media in mediaList:
            mediaExt = os.path.splitext(media)[-1][1:].lower()
            if os.path.isfile(file) and mediaExt in AUDIO + IMAGE:
                mediaPath = os.path.join(mediaDir, media)
                mediaName = mw.col.media.addFile(mediaPath)
                mediaRelativePath = os.path.join(os.path.basename(mediaDir), media)
                if mediaExt in AUDIO:
                    mediaDict[mediaRelativePath] = (mediaName, 'AUDIO')
                else:
                    mediaDict[mediaRelativePath] = (mediaName, 'IMAGE')
        source = addMediaPointer(source, mediaDict)
        QAList = getQAFromHTML(source)
        tagList = getTagsFromHTML(source)
    elif os.path.splitext(file)[-1] == '.md':
        f = open(file, encoding = 'utf-8', mode = 'r')
        source = f.read()
        f.close()
        QAList = getQAFromMarkdown(source, level)
        metaDict = getMetaFromMarkdowm(source)
        ACTIONS += metaDict.keys()
    mw.progress.start(max=len(QAList), parent=mw, immediate=True)
    newCount = 0
    for i, QA in enumerate(QAList):
        note = notes.Note(mw.col, model)
        note.model()['did'] = did
        for (field, actionIdx, special) in fieldList:
            action = ACTIONS[actionIdx]
            if not action:
                continue
            elif action == '问题':
                data = QA[0]
            elif action == '答案':
                data = QA[1]
            elif action == '标签':
                data = ' '.join(tagList)
            else:
                data = metaDict[action]
            if special and field == 'Tags':
                note.tags.append(data)
            else:
                note[field] = data
        if not mw.col.addNote(note):
            showFailureDialog('无法访问 Anki 数据库')
            return
        newCount += 1
        mw.progress.update(value=i)
    mw.progress.finish()
    # 刷新界面，使得卡组显示新增的卡片数
    mw.reset()
    showCompletionDialog(newCount)

class ImportSettingsDialog(QDialog):
    def __init__(self):
        global mw
        QDialog.__init__(self, mw)
        self.mw = mw
        self.form = dialog.Ui_Form()
        self.form.setupUi(self)
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(self.reject)
        self.form.browse.clicked.connect(self.onBrowse)
        self.deck = DeckChooser(self.mw, self.form.deckArea, label=False)
        # The path to the media directory chosen by user
        self.mediaDir = None
        # The number of fields in the note type we are using
        self.fieldCount = 0
        self.populateModelList()
        self.exec_()

    def populateModelList(self):
        """Fill in the list of available note types to select from."""
        models = mw.col.models.all()
        for m in models:
            item = QListWidgetItem(m['name'])
            # Put the model in the widget to conveniently fetch later
            item.model = m
            self.form.modelList.addItem(item)
        self.form.modelList.sortItems()
        self.form.modelList.currentRowChanged.connect(self.populateFieldGrid)
        # Triggers a selection so the fields will be populated
        self.form.modelList.setCurrentRow(0)

    def populateFieldGrid(self):
        """Fill in the fieldMapGrid QGridLayout.

        Each row in the grid contains two columns:
        Column 0 = QLabel with name of field
        Column 1 = QComboBox with selection of mappings ("actions")
        The first two fields will default to Media and File Name, so we have
        special cases for rows 0 and 1. The final row is a spacer."""

        self.clearLayout(self.form.fieldMapGrid)
        # Add note fields to grid
        row = 0
        for field in self.form.modelList.currentItem().model['flds']:
            self.createRow(field['name'], row)
            row += 1
        # Add special fields to grid
        for name in SPECIAL_FIELDS:
            self.createRow(name, row, special=True)
            row += 1
        self.fieldCount = row
        self.form.fieldMapGrid.addItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), row, 0)

    def createRow(self, name, idx, special=False):
        lbl = QLabel(name)
        cmb = QComboBox()
        cmb.addItems(ACTIONS)
        # piggy-back the special flag on QLabel
        lbl.special = special
        self.form.fieldMapGrid.addWidget(lbl, idx, 0)
        self.form.fieldMapGrid.addWidget(cmb, idx, 1)
        if idx == 0: cmb.setCurrentIndex(1)
        if idx == 1: cmb.setCurrentIndex(2)

    def getDialogResult(self):
        """
        将用户在界面中保存的设置作为一个元组返回。元组包含以下内容：
        - 文件路径
        - 卡组
        - 笔记类型
        - 导入信息与笔记类型各领域的对应关系
        - 是否导入
        """

        if self.result() == QDialog.Rejected: return None, None, None, None, False

        model = self.form.modelList.currentItem().model
        # Iterate the grid rows to populate the field map
        fieldList = []
        did = self.deck.selectedId()
        grid = self.form.fieldMapGrid
        for row in range(self.fieldCount):
            # QLabel with field name
            field = grid.itemAtPosition(row, 0).widget().text()
            # Piggy-backed special flag
            special = grid.itemAtPosition(row, 0).widget().special
            # QComboBox with index from the action list
            actionIdx = grid.itemAtPosition(row, 1).widget().currentIndex()
            fieldList.append((field, actionIdx, special))
        return self.mediaDir, did, model, fieldList, True

    def onBrowse(self):
        """
        Show the directory selection dialog.
        """
        path = QFileDialog.getOpenFileName(mw, caption = '导入文件', filter = '文本文件 (*.html *.md)')[0]
        if not path:
            return
        self.mediaDir = path
        self.form.mediaDir.setText(self.mediaDir)
        self.form.mediaDir.setStyleSheet("")

    def accept(self):
        """
        如果用户没有选择就导入，那么不接受此消息并将文件名的边框设为红色。
        """
        if not self.mediaDir:
            self.form.mediaDir.setStyleSheet("border: 1px solid red")
            return
        QDialog.accept(self)

    def clearLayout(self, layout):
        """
        Convenience method to remove child widgets from a layout.
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())

def showCompletionDialog(newCount):
    QMessageBox.about(mw, "笔记导入成功", "完成笔记导入，共生成了 %d 条新笔记。" % newCount)

def showFailureDialog(reason):
    QMessageBox.about(mw, "笔记导入失败", "没有生成笔记。原因是：%s。" % reason)

action = QAction('从 HTML 或 Markdown 文档导入……', mw)
action.triggered.connect(doImport)
mw.form.menuTools.addAction(action)