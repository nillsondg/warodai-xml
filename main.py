import glob
import os
import re
from lxml import etree

# Конвертация словаря Warodai в формат xml, согласно формату
# https://warodai.ru/about/readme
# todo 3.4.3. Обозначение омограмм римскими цифрами
# todo 3.7. Гнездование
# todo 3.8. Общее уточнение
# todo そう【添う】(соу)〔002-52-52〕
#  (に)
warodai_dir = "/Users/dmitry/Documents/GitHub/warodai-source/"


def convert_warodai_to_xml():
    root = etree.Element("warodai")
    count = 0
    for filename in glob.iglob(warodai_dir + '**/*.txt', recursive=True):
        article = read_article(filename)
        article_name = os.path.basename(filename).split(".")[0]
        parse_article(article_name, article, root)
        count += 1

    xml_tree = etree.ElementTree(root)
    with open('./warodai.xml', 'wb') as f:
        f.write(etree.tostring(xml_tree, encoding="UTF-8"))
    print(f'converted {count} articles')


def read_article(filename):
    with open(f'{filename}', 'r') as f:
        return f.read()


def parse_article(name, article, root):
    print("parse_article " + name)
    split = article.split("\n")
    title = split[0]
    rubrics = split[1:]
    xml_article = etree.SubElement(root, "article")
    parse_title(title, xml_article)
    parse_rubrics(rubrics, xml_article)


def parse_title(title, article_element):
    # check https://github.com/warodai/txt_builder/blob/feb8acc7cdda7bb3d29add1c7d98eddb295839f6/builder.php#L196
    title_match = re.search(r'^([^【(]*)(【([\S ]*)】)?\((.*)\)\s?(\[([ёа-яЁА-Я.:; ]*)\])?\s?〔(\S*)〕', title)
    kana = title_match.group(1)
    hyoukies = title_match.group(3)
    kiriji = title_match.group(4)
    corpus = title_match.group(6)
    number = title_match.group(7)

    article_element.set("kana", kana)
    if hyoukies is not None:
        for hyouki in hyoukies.split("･"):
            etree.SubElement(article_element, "hyouki").text = hyouki
    article_element.set("kiriji", kiriji)
    if corpus is not None:
        article_element.set("corpus", corpus)
    article_element.set("number", number)


def parse_rubrics(rubrics, article_element):
    rubric_element = None
    group = None
    for line in rubrics:
        if line == "":
            continue
        rubric_match = re.search(r'^(\d)[).]\s*(.*)', line)
        derivative_rubric_match = re.search(r'^: ～', line)
        if rubric_match is not None:
            meaning = rubric_match.group(2)
            if meaning == '':
                group = rubric_match.group(1)
                continue
            rubric_element = etree.SubElement(article_element, "rubric")
            if group is not None:
                rubric_element.set("group", group)
            rubric_element.text = clear_line(meaning)
            continue

        derivative_match = re.search(r'^～', line)
        idiom_match = re.search(r'^◇', line)

        text = clear_line(line)
        if rubric_element is None:
            rubric_element = etree.SubElement(article_element, "rubric")
            if derivative_rubric_match is not None:
                rubric_element.set("type", "derivative")
            rubric_element.text = text
            continue
        if derivative_match is not None:
            derivative_element = etree.SubElement(rubric_element, "derivative")
            derivative_element.text = text
            continue

        phrase_element = etree.SubElement(rubric_element, "phrase")
        phrase_element.text = text
        if idiom_match is not None:
            phrase_element.set("type", "idiom")
            rubric_element.text = clear_line(text)
            continue


def clear_line(line):
    if line[-1] in set("."";"):
        return line[:-1]
    return line


def test_parse():
    test_root = etree.Element("warodai")
    filename = warodai_dir + "006/49/006-49-94.txt"
    # filename = warodai_dir + "000/12/000-12-70.txt"
    filename = warodai_dir + "008/28/008-28-35.txt"
    filename = warodai_dir + "007/61/007-61-37.txt"
    filename = warodai_dir + "002/52/002-52-52.txt"
    article_name = os.path.basename(filename).split(".")[0]
    article = read_article(filename)
    parse_article(article_name, article, test_root)
    xml_tree = etree.ElementTree(test_root)
    with open('./warodai_test.xml', 'wb') as f:
        f.write(etree.tostring(xml_tree, encoding="UTF-8"))


if __name__ == '__main__':
    convert_warodai_to_xml()
    # test_parse()
