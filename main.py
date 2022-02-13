import glob
import json
import os
import re
from lxml import etree


def parse():
    warodai_dir = "/Users/dmitry/Documents/GitHub/warodai-source/"
    # article = read_article("000-10-52.txt")

    # article = read_article(warodai_dir + "000/61/" + "000-61-84.txt")
    # parse_article(article)
    #

    root = etree.Element("warodai")

    for filename in glob.iglob(warodai_dir + '**/*.txt', recursive=True):
        article = read_article(filename)
        article_name = os.path.basename(filename).split(".")[0]
        parse_article(article_name, article, root)

    xml_tree = etree.ElementTree(root)
    with open('./warodai.xml', 'wb') as f:
        f.write(etree.tostring(xml_tree, encoding="UTF-8"))


def read_article(filename):
    with open(f'{filename}', 'r') as f:
        return f.read()


def parse_article(name, article, root):
    print("parse_article " + name)
    title = article.split("\n")[0]
    xml_article = etree.SubElement(root, "article")
    parse_title(title, xml_article)


def parse_title(title, article_element):
    # check https://github.com/warodai/txt_builder/blob/feb8acc7cdda7bb3d29add1c7d98eddb295839f6/builder.php#L196
    m = re.search(r'^([^【(]*)(【([\S ]*)】)?\((.*)\)\s?(\[([ёа-яЁА-Я.:; ]*)\])?\s?〔(\S*)〕', title)
    kana = m.group(1)
    kanji = m.group(3)
    kiriji = m.group(4)
    corpus = m.group(6)
    number = m.group(7)

    article_element.set("kana", kana)
    if kanji is not None:
        article_element.set("hyouki", kanji)
    article_element.set("kiriji", kiriji)
    if corpus is not None:
        article_element.set("corpus", corpus)
    article_element.set("number", number)


if __name__ == '__main__':
    parse()
