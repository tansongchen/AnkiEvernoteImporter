# Evernote2Anki

与小能熊「知识内化训练营」配套的笔记自动化导入插件。源代码由两个文件组成：

1. `__init__.py`：展示导入界面，操作数据库
2. `dialog.ui`：导入界面的具体配置

而 `dialog.py` 是用 `PyQt` 自动生成的界面程序。编译命令为：

```bash
pyuic -o dialog.py dialog.ui
```

`/old/` 中存放了以前的一些自动化的尝试，供参考。

`/bs4/` 是本插件所依赖的 Beautiful Soup 库。

