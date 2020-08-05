from markdown import markdown

with open('README.md') as f:
    md = f.read()

with open('README.html', 'w') as f:
    html = markdown(md)
    f.write(html)
