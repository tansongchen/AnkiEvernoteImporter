'''
实现印象笔记中的普通笔记、Markdown 笔记和超级笔记的 Anki 自动导入
'''

import os
from bs4 import BeautifulSoup
from aqt import mw
from aqt.qt import *
from aqt.deckchooser import DeckChooser
from aqt.editor import audio, pics
from anki import notes
from .dialog import Ui_Form
from .preprocessor import preprocess
from .qa import split, splitLegacy, updateMedia

ACTIONS = ['', '问题', '答案']
SPECIAL_FIELDS = ['Tags']

class ImportSettingsDialog(QDialog):
    def __init__(self):
        global mw
        QDialog.__init__(self, mw)
        self.mw = mw
        self.form = Ui_Form()
        self.form.setupUi(self)
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(self.reject)
        self.form.browse.clicked.connect(self.onBrowse)
        self.deck = DeckChooser(self.mw, self.form.deckArea, label=False)
        # The path to the media directory chosen by user
        self.fileName = None
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
        - 分割层级
        - 是否导入
        """

        if self.result() == QDialog.Rejected:
            return None, None, None, None, None, False

        model = self.form.modelList.currentItem().model
        # Iterate the grid rows to populate the field map
        fieldList = []
        did = self.deck.selectedId()
        level = int(self.form.level.currentText())
        grid = self.form.fieldMapGrid
        for row in range(self.fieldCount):
            # QLabel with field name
            field = grid.itemAtPosition(row, 0).widget().text()
            # Piggy-backed special flag
            special = grid.itemAtPosition(row, 0).widget().special
            # QComboBox with index from the action list
            actionIdx = grid.itemAtPosition(row, 1).widget().currentIndex()
            fieldList.append((field, actionIdx, special))
        return self.fileName, did, model, fieldList, level, True

    def onBrowse(self):
        """
        Show the directory selection dialog.
        """
        fileName = QFileDialog.getOpenFileName(mw, caption='导入文件', filter='文本文件 (*.html *.md)')[0]
        if not fileName:
            return
        self.fileName = fileName
        self.form.mediaDir.setText(fileName)
        self.form.mediaDir.setStyleSheet("")

    def accept(self):
        """
        如果用户没有选择就导入，那么不接受此消息并将文件名的边框设为红色。
        """
        if not self.fileName:
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
    QMessageBox.about(mw, '笔记导入成功', '完成笔记导入，共生成了 %d 条新笔记。' % newCount)

def showFailureDialog(reason):
    QMessageBox.about(mw, '笔记导入失败', '没有生成笔记。原因是：%s。' % reason)

def extractFrom(fileName, level):
    fileBaseName, fileExt = os.path.splitext(fileName)
    with open(fileName, encoding='utf-8', mode='r') as f:
        text = f.read()
    if fileExt == '.html':
        # 检查同目录下是否有 Evernote 自动生成的 .resources 目录，如果有则导入媒体文件，如果没有则不导入
        if os.path.exists('%s.resources' % fileBaseName):
            mediaDir = '%s.resources' % fileBaseName
            mediaList = os.listdir(mediaDir)
        elif os.path.exists('%s_files' % fileBaseName):
            mediaDir = '%s_files' % fileBaseName
            mediaList = os.listdir(mediaDir)
        else:
            mediaList = []
        audioDict = {}
        picsDict = {}
        for media in mediaList:
            mediaExt = os.path.splitext(media)[-1][1:].lower()
            if mediaExt in audio + pics:
                mediaPath = os.path.join(mediaDir, media)
                mediaName = mw.col.media.addFile(mediaPath)
                mediaRelativePath = '%s/%s' % (os.path.basename(mediaDir), media)
                if mediaExt in audio:
                    audioDict[mediaRelativePath] = mediaName
                else:
                    picsDict[mediaRelativePath] = mediaName
        soup = BeautifulSoup(text, 'html.parser')
        updateMedia(soup, audioDict, picsDict)
        if soup.select_one('head meta[name="content-class"]')['content'] == 'yinxiang.superNote':
            return split(soup, level)
        else:
            return splitLegacy(soup)
    elif fileExt == '.md':
        html = preprocess(text)
        soup = BeautifulSoup(html, 'html.parser')
        return split(soup, level)
    else:
        return []

def doImport():
    fileName, did, model, fieldList, level, ok = ImportSettingsDialog().getDialogResult()
    if not ok: return
    qaList = extractFrom(fileName, level)
    mw.progress.start(max=len(qaList), parent=mw, immediate=True)
    newCount = 0
    for i, qa in enumerate(qaList):
        note = notes.Note(mw.col, model)
        note.model()['did'] = did
        for field, actionIndex, special in fieldList:
            action = ACTIONS[actionIndex]
            if action == '问题':
                data = qa.question
            elif action == '答案':
                data = qa.answer
            else:
                continue
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
    mw.reset()
    showCompletionDialog(newCount)

menu = QAction('从 HTML 或 Markdown 文档导入……', mw)
menu.triggered.connect(doImport)
mw.form.menuTools.addAction(menu)
