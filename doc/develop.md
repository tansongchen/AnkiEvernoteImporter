# 搭建 Anki 开发环境

```bash
pip install -r REQUIREMENTS.txt
```

# 插件开发

```bash
pyuic5 -o src/dialog.py src/dialog.ui
```

# 部署

```bash
mkdir dist
ln -s <ankidir>/addons21/Evernote2Anki dist
cp src/*.py dist/
```

# 打包发布

