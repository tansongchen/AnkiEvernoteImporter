from PIL import Image
import os, sys

# 辅助函数
def a(t, u, v): #造轮子，向量加法
    return (t[0]+u, t[1]+v)

def p(sp, box): #把起始点和方块大小转化为 crop 需要的参数形式
    return (sp[0], sp[1], sp[0]+box[0], sp[1]+box[1])

def split_image(im, paras):
    l, r, b, s = paras[1:]
    p1 = im.crop(p(l,s))
    p2 = im.crop(p(a(l, 0, s[1]), s))
    p3 = im.crop(p(a(l, s[0]-20, 0), s))
    p4 = im.crop(p(a(l, s[0]-20, s[1]), s))
    p5 = im.crop(p(r,s))
    p6 = im.crop(p(a(r, 0, s[1]), s))
    p7 = im.crop(p(a(r, s[0]-20, 0), s))
    p8 = im.crop(p(a(r, s[0]-20, s[1]), s))
    p14 = im.crop(p(l,b))
    p58 = im.crop(p(r,b))
    return [im, p1, p2, p3, p4, p5, p6, p7, p8, p14, p58]

def gen_info(course, ims, mode, cards, form):
    im, p1, p2, p3, p4, p5, p6, p7, p8, p14, p58 = ims
    info_list_a = []
    if mode == 'full':
        iml = [im]
    elif mode == 'split':
        iml = [p1, p2, p3, p4, p5, p6, p7, p8]
    elif mode == 'left':
        iml = [p14, p5, p6, p7, p8]
    else:
        iml = [p1, p2, p3, p4, p58]
    cardl = cards.split('|')
    for index in range(len(iml)):
        card = cardl[index]
        if card:
            name = 'NOTE' + course[:3] + card + '.' + form
            pos, que = card.split()
            html = '<img src="' + name + '">'
            info_list_a.append((name, pos, que, html, iml[index], ''))
    return info_list_a

def write_import(info_list, root):
    f = open(root + '/导入.txt', encoding = 'utf-8', mode = 'w')
    for i in info_list:
        name, pos, que, html, img, per = i
        f.write('\t'.join((pos, que, html, per))+'\n')
    f.close()

def write_media(info_list):
    for i in info_list:
        name, pos, que, html, img, per = i
        img.save(media + '/' + name)

def read_note_paras(course):
    root = '/Users/tansongchen/文档/' + course
    f = open(root + '/笔记参数.txt', encoding = 'utf-8', mode = 'r')
    paras = tuple(tuple(map(int, line.strip('\r\n').split())) for line in f)
    return paras

def main(course):
    root = '/Users/tansongchen/文档/' + course
    paras = read_note_paras(course)
    info_list = []
    f = open(root + '/笔记.txt', encoding = 'utf-8', mode = 'r')
    for line in f:
        num, form, mode, cards = line.strip('\r\n').split('\t')
        cardl = [x for x in cards.split('|') if x != '']
        r = all(map(lambda x: 'NOTE'+course[:3]+x+'.jpg' in exist_image, cardl))
        if 1:
            im = Image.open(root + '/笔记/' + num + '.' + form)
            im = im.rotate(270, expand = True)
            im = im.resize(paras[0])
            ims = split_image(im, paras)
            info_list += gen_info(course, ims, mode, cards, form)
    f.close()

    write_media(info_list)
    write_import(info_list, root)

# 本学期有三门课程这样处理笔记
media = '/Users/tansongchen/Library/Application Support/Anki2/Songchen Tan/collection.media'
exist_image = list(filter(lambda x: x[:4] == 'NOTE', os.listdir(media)))
# courses = ['102 - 高等代数', '135 - 数学物理方法', '136 - 理论力学']
courses = ['102 - 高等代数']
for course in courses:
    main(course)
