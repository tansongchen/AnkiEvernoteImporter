# 搭建 Anki 开发环境

将源代码克隆至本地：

```bash
git clone https://github.com/tansongchen/AnkiEvernoteImporter.git
cd AnkiEvernoteImporter
```

## 安装依赖（自动）

所有依赖均位于 `REQUIREMENTS.txt` 中，可以用 `pip` 一次性安装：

```bash
pip install -r REQUIREMENTS.txt
```

## 安装依赖（手动）

用上面这种方法安装的依赖包含了全部 Anki 2.1.x 的源代码，不过这些代码仅用于 Visual Studio Code 的代码提示功能，实际并不会用到。如果不需要此功能，可以只安装以下四个包：

```bash
pip install bs4 markdown pyqt5 pygments
```

# 开发

## `dialog.ui`

本插件包含一个导入对话框，该对话框的界面由 `dialog.ui` 定义，你可以下载 [Qt Designer](https://build-system.fman.io/qt-designer-download) 来编辑。编辑完成后，利用

```bash
pyuic5 src/dialog.ui -o src/dialog.py
```

生成 `dialog.py` 文件。由于它是自动生成的，请不要在其中作任何手动修改。

## `preprocessor.py`

`preprocessor.preprocess(text)` 负责将 Markdown 文本转化为 HTML 文本。这一转换依赖于 `markdown` 包，Anki 发行版已经包含了这个包，所以不需要与插件一同打包。但是，这一转换用到了插件 `CodeHiliteExtension`，它需要我们安装 `pygments`，因此我们需要将 `pygments` 随插件安装。

## `qa.py`

- `qa.split(soup, level)`：将 HTML 转换为由 Q & A 笔记构成的列表；
- `qa.updateMedia(soup, audioDict, picsDict)`：更新 HTML 中指向媒体文件的链接；
- `qa.splitLegacy(soup)`：类似于 `qa.split`，用于转换印象笔记中的普通笔记，但该功能已经暂停维护。

## `__init__.py`

完成最终的导入工作。

# 部署测试

## macOS 或 Linux 上的部署测试

首先在项目根目录下建立一个新文件夹：

```bash
mkdir dist
```

在 macOS 或者 Linux 上，你可以在 Anki 插件文件夹里创建一个指向该文件夹的软链接，例如在 macOS 上可以使用

```bash
ln -s ~/Library/Application\ Support/Anki2/addons21/test dist
```

然后，我们每次部署的时候，只需要将插件的四个源码文件和 `pygments` 包复制到该目录即可。

```bash
cp src/*.py dist/
cp -r <pythonenv>/lib/python3.7/site-packages/pygments dist/
```

其中 `<pythonenv>` 是你使用的 Python 环境目录，如果你不知道这个目录是什么的话，可以试试 `pip install pygments`，它会提示你该包已经安装在某个目录。

## Windows 上的部署测试

你可以在 Anki 插件文件夹中创建一个新文件夹 `test`，将插件的四个源码文件和 `pygments` 包手动复制到该目录。
