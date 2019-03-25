from PIL import Image
import os, sys

# Part 1 辅助函数
def a(t, u, v): #造轮子，向量加法
    return (t[0]+u, t[1]+v)

def p(sp, box): #把起始点坐标 (x,y) 和方块大小 (dx,dy) 转化为 crop 需要的参数形式
    return (sp[0], sp[1], sp[0]+box[0], sp[1]+box[1])

# Part 2 功能函数
def split_image(im, paras): #根据切割参数把图片切成11份
    """
    paras 结构如下：
    paras = (a, l, r, b, s)
    l是左半页左上角的坐标，r是右半页左上角的坐标。b是一页纸的大小，s是四分之一页纸的大小。
    lrbs都是二维向量。
    """
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

def gen_info_and_media(course, ims, mode, cardl, form):
    """
    输入：课程名称，切好的图片列表，切分模式，卡片列表，图片格式
    输出：
    1. 用于导入这些卡片到 Anki 中的信息
    2. 要写入到 Anki 的 media 文件夹的图片
    """
    im, p1, p2, p3, p4, p5, p6, p7, p8, p14, p58 = ims
    info_list_add, media_list_add = [], []
    if mode == 'full':
        iml = [im]
    elif mode == 'split':
        iml = [p1, p2, p3, p4, p5, p6, p7, p8]
    elif mode == 'left':
        iml = [p14, p5, p6, p7, p8]
    else:
        iml = [p1, p2, p3, p4, p58]
    for index in range(len(iml)):
        try:
            card = cardl[index]
        except IndexError:
            print(cardl)
        if card:
            name = 'NOTE' + course[:3] + card + '.' + form
            try:
                pos, que = card.split(' ')
            except ValueError:
                print(card)
            iden = 'NOTE' + course[:3] + pos
            html = '<img src="' + name + '">'
            info_list_add.append((iden, pos, que, html, ''))
            media_list_add.append((name, iml[index]))
    return info_list_add, media_list_add

# Part 3 输入输出函数
def write_import(info_list, root): #把信息写到导入文件中
    f = open(root + '/导入.txt', encoding = 'utf-8', mode = 'w')
    f.write('\n'.join('\t'.join(i) for i in info_list))
    f.close()

def write_media(media_list): #把图片写到媒体文件夹中
    for i in media_list:
        name, img = i
        if img != None:
            img.save(media + '/' + name)

def read_note_paras(course): #读取笔记参数
    root = '/Users/tansongchen/documents/' + course
    f = open(root + '/笔记参数.txt', encoding = 'utf-8', mode = 'r')
    paras = tuple(tuple(map(int, line.strip('\r\n').split())) for line in f)
    return paras

# Part 4 主操作函数，函数是针对一门课而言的
def main(course):
    root = '/Users/tansongchen/documents/' + course
    paras = read_note_paras(course)
    info_list, media_list = [], []
    f = open(root + '/笔记.txt', encoding = 'utf-8', mode = 'r')
    for line in f:
        num, form, mode, cards = line.strip('\r\n').split('\t')
        cardl = cards.split('｜')
        realcardl = [x for x in cardl if x != '']
        r = all(map(lambda x: 'NOTE'+course[:3]+x+'.'+form in exist_image, realcardl))
        if r:
            ims = [None]*11
        else:
            im = Image.open(root + '/笔记/' + num + '.' + form)
            im = im.rotate(270, expand = True)
            im = im.resize(paras[0])
            ims = split_image(im, paras)
        info_list_add, media_list_add = gen_info_and_media(course, ims, mode, cardl, form)
        info_list += info_list_add
        media_list += media_list_add
    f.close()
    
    write_media(media_list)
    write_import(info_list, root)

# Part 5 主程序，定义了本学期有三门课程这样处理笔记
media = '/Users/tansongchen/Library/Application Support/Anki2/Songchen Tan/collection.media'
exist_image = list(filter(lambda x: x[:4] == 'NOTE', os.listdir(media)))
courses = ['102 - 高等代数', '135 - 数学物理方法', '136 - 理论力学']
for course in courses:
    main(course)
