# -*- coding: utf-8 -*-

from aqt import mw
from aqt.qt import *
from aqt.deckchooser import DeckChooser
from aqt import editor
from anki import notes
from bs4 import BeautifulSoup
from . import dialog

# Possible field mappings
ACTIONS = ['', 'Q', 'A']

# Note items that we can import into that are not note fields
SPECIAL_FIELDS = ['Tags']

def doMediaImport():
    # Raise the main dialog for the add-on and retrieve its result when closed.
    # (path, model, fieldList, ok) = ImportSettingsDialog().getDialogResult()
    (HTMLFile, did, model, fieldList, ok) = ImportSettingsDialog().getDialogResult()
    if not ok:
        return
    mw.progress.start(max=1, parent=mw, immediate=True)
    newCount = 0
    failure = False
    f = open(HTMLFile, encoding = 'utf-8', mode = 'r')
    HTML = f.read()
    f.close()
    note = notes.Note(mw.col, model)
    note.model()['did'] = did
    for (field, actionIdx, special) in fieldList:
        action = ACTIONS[actionIdx]
        if action == '':
            continue
        elif action == "Q":
            data = 'Q'
        elif action == "A":
            data = 'A'

        if special and field == "Tags":
            note.tags.append(data)
        else:
            note[field] = data
    if not mw.col.addNote(note):
        failure = True
    newCount += 1
    # mw.progress.update(value=i)
    mw.progress.finish()
    mw.deckBrowser.refresh()
    if failure:
        showFailureDialog()
    else:
        showCompletionDialog(newCount, did)

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
        """Return a tuple containing the user-defined settings to follow
        for an import. The tuple contains four items (in order):
         - Path to chosen media directory
         - The model (note type) to use for new notes
         - A dictionary that maps each of the fields in the model to an
           integer index from the ACTIONS list
         - True/False indicating whether the user clicked OK/Cancel"""

        if self.result() == QDialog.Rejected:
            return None, None, None, None, False

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
        """Show the directory selection dialog."""
        path = QFileDialog.getOpenFileName(mw, "Import Directory")[0]
        if not path:
            return
        self.mediaDir = path
        self.form.mediaDir.setText(self.mediaDir)
        self.form.mediaDir.setStyleSheet("")

    def accept(self):
        # Show a red warning box if the user tries to import without selecting
        # a directory.
        if not self.mediaDir:
            self.form.mediaDir.setStyleSheet("border: 1px solid red")
            return
        QDialog.accept(self)

    def clearLayout(self, layout):
        """Convenience method to remove child widgets from a layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())


def showCompletionDialog(newCount, did):
    QMessageBox.about(mw, "笔记导入成功",
"""
<p>
完成笔记导入，共生成了 %s 条新笔记。
所有生成的笔记位于 %s 卡组中。
</p>""" % newCount, did)

def showFailureDialog():
    QMessageBox.about(mw, "笔记导入失败",
"""
<p>
没有生成相应卡片。
</p>
""")

action = QAction("Q&A 笔记导入", mw)
action.triggered.connect(doMediaImport)
mw.form.menuTools.addAction(action)