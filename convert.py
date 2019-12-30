from routines import getQAFromMarkdown
import sys
with open(sys.argv[1], encoding='utf-8', mode='r') as f:
    MD = f.read()
QAList = getQAFromMarkdown(MD, 2)
with open('import.txt', encoding='utf-8', mode='w') as f:
    for QA in QAList: f.write('\t'.join(QA) + '\n')