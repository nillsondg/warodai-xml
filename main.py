import glob
import os
import re
from datetime import date

from lxml import etree

# Конвертация словаря Warodai в формат xml, согласно формату
# https://warodai.ru/about/readme
# todo 3.4.3. Обозначение омограмм римскими цифрами
# todo 3.7. Гнездование
warodai_dir = "/Users/dmitry/Documents/GitHub/warodai-source/"


def convert_warodai_to_xml():
    root = etree.Element("warodai")
    count = 0
    for filename in glob.iglob(warodai_dir + '**/*.txt', recursive=True):
        article = read_article(filename)
        article_name = os.path.basename(filename).split(".")[0]
        parse_article(article_name, article, root)
        count += 1

    root = etree.ElementTree(root)
    today = date.today().isoformat()
    with open(f'./warodai{today}.xml', 'wb') as f:
        f.write(etree.tostring(root, encoding="UTF-8", pretty_print=True))
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

    article_element.set("kana", remove_homogram(kana))
    if hyoukies is not None:
        for hyouki in hyoukies.split("･"):
            etree.SubElement(article_element, "hyouki").text = remove_homogram(hyouki)
    article_element.set("kiriji", kiriji)
    if corpus is not None:
        article_element.set("corpus", corpus)
    article_element.set("number", number)


def parse_rubrics(rubrics, article_element):
    rubric_element = None
    group = None
    litter = None
    litter_kanji = ""
    for line in rubrics:
        if line == "":
            continue
        rubric_match = re.search(r'^(\d)[).]\s*(.*)', line)
        if rubric_match is not None:
            meaning = clear_line(rubric_match.group(2))
            if meaning == '':
                group = rubric_match.group(1)
                continue
            rubric_element = etree.SubElement(article_element, "rubric")
            if group is not None:
                rubric_element.set("group", group)
            if litter is not None or litter_kanji != '':
                litter_match = None
                if litter is not None:
                    litter_match = re.match(r'(<i>)([ёЁа-яА-Я ]*\.):?(</i>)', litter)
                meaning_with_litter_m = re.search(
                    r'((<i>)(?P<corpus>[ёЁа-яА-Я. ]*)(</i>))?((?P<deri>: ～[一-龯ぁ-んァ-ン]*)|(?P<kanji>[一-龯ぁ-んァ-ン]*))?(?P<comma>: )?(?P<meaning>.*)$',
                    meaning)
                if litter_match is not None and meaning_with_litter_m is not None:
                    # print(litter_match.groups())
                    # print(meaning_with_litter_m.groups())
                    meaning = " ".join(filter(None, [meaning_with_litter_m.expand(r"\g<deri>"),
                                                     litter_kanji,
                                                     litter_match.expand(r"\g<1>\g<2>"),
                                                     meaning_with_litter_m.expand(r"\g<corpus>\g<comma>"),
                                                     litter_match.expand(r"\g<3>"),
                                                     meaning_with_litter_m.expand(r"\g<kanji>"),
                                                     meaning_with_litter_m.group("meaning")]))
                elif litter is not None:
                    meaning = litter + " " + meaning
                elif len(litter_kanji) > 0 and meaning_with_litter_m is not None:
                    meaning = meaning_with_litter_m.expand(r"\g<deri> ") + litter_kanji \
                              + meaning_with_litter_m.expand(r"\g<1> \g<meaning>")
                    meaning = meaning.strip()
                else:
                    raise RuntimeError("litter process failed")
            rubric_element.text = meaning
            continue

        if rubric_element is None:
            litter_kanji_m = re.fullmatch(r'^\(?((<i>)([ёЁа-яА-Яa-zA-Z]*\.)(</i>) [一-龯ぁ-んァ-ンА-Яа-яЁё]*)\)?$', line)
            if litter_kanji_m is not None:
                litter_kanji = litter_kanji_m.expand(r"(\g<1>)")
                continue
            # search из-за (<i>нем.</i> Aphtha[e]) <i>мед.</i>
            litter_match = re.search(r'(<i>)([ ёЁа-яА-Яa-zA-Z]*\.:?)(</i>)$', line)
            litter_derivative_match = re.match(r'^: ～[一-龯ぁ-んァ-ン]*', line) or re.fullmatch(r'\(\S*\)', line)
            if litter_match is not None:
                litter = line
                continue
            if litter_derivative_match is not None:
                litter = line
                continue

        derivative_match = re.search(r'^～', line)
        idiom_match = re.search(r'^◇', line)

        text = clear_line(line)
        if rubric_element is None:
            rubric_element = etree.SubElement(article_element, "rubric")
            if derivative_match is None:
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
            rubric_element.text = text
            continue


def clear_line(line):
    if len(line) == 0:
        return line
    if line[-1] in set("."";"):
        return line[:-1].strip()
    return line.strip()


def remove_homogram(text):
    homogram_m = re.search(r"([一-龯ぁ-んァ-ンゝ]+)(I+)(.*)", text)
    if homogram_m is None:
        return text
    return homogram_m.expand(r"\g<1>\g<3>")


def test_parse():
    test_root = etree.Element("warodai")
    files = [
        # "004-23-67",
        # "006-79-94",
        # "005-75-60",
        # "008-56-59",
        # "007-58-00",
        # "002-52-52",
        # "005-78-01",
        # "004-94-80",
        # "006-07-86",
        "007-61-80"
    ]
    for filename in files:
        numbers = filename.split("-")
        file = f"{warodai_dir}/{numbers[0]}/{numbers[1]}/{filename}.txt"
        article_name = os.path.basename(file).split(".")[0]
        article = read_article(file)
        parse_article(article_name, article, test_root)
    root = etree.ElementTree(test_root)
    root.write('./warodai_test.xml', encoding="utf-8", pretty_print=True, method="xml")


if __name__ == '__main__':
    convert_warodai_to_xml()
    # test_parse()
