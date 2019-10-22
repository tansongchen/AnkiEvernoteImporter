import shutil
import os

addOnFolder = '/Users/tansongchen/Library/Application Support/Anki2/addons21/Evernote2Anki/'
os.system('pyuic5 -o dialog.py dialog.ui')
for file in ['__init__.py', 'dialog.py', 'dialog.ui', 'routines.py']:
    shutil.copyfile(file, addOnFolder + file)