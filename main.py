import glob
import os
import re
from datetime import date
from lxml import etree

# Конвертация словаря Warodai в формат xml, согласно формату
# https://warodai.ru/about/readme
# todo 3.12. Общие отсылки (ср.)
# подсказки по классам японских символов regex https://gist.github.com/terrancesnyder/1345094
warodai_dir = "/Users/dmitry/Documents/GitHub/warodai-source/"

export_count = 0


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
    print(f'exported {export_count} articles')


def read_article(filename):
    with open(f'{filename}', 'r') as f:
        return f.read()


def parse_article(name, article, root):
    global export_count
    print("parse_article " + name)
    split = article.split("\n")
    title = split[0]
    rubrics = split[1:]

    # check https://github.com/warodai/txt_builder/blob/feb8acc7cdda7bb3d29add1c7d98eddb295839f6/builder.php#L196
    title_match = re.search(
        r'^(?P<kana>[^【(]*)(【(?P<hyoukies>[\S ]*)】)?\((?P<kiriji>.*)\)\s?(\[(?P<corpus>[ёа-яЁА-Я.:; ]*)\])?\s?〔(?P<number>\S*)〕',
        title)
    kanas = title_match.group("kana")
    hyoukies = title_match.group("hyoukies")
    kirijies = title_match.group("kiriji")
    corpus = title_match.group("corpus")
    number = title_match.group("number")

    kana_nesting = kanas.count(", ")
    hyouki_nesting = hyoukies.count(", ") if hyoukies is not None else 0
    if 0 < kana_nesting == hyouki_nesting > 0:
        kana_list = kanas.split(", ")
        hyouki_list = hyoukies.split(", ")
        kiriji_list = kirijies.split(", ")
        for nest_i in range(kana_nesting + 1):
            kana = kana_list[nest_i]
            hyouki = hyouki_list[nest_i]
            kiriji = kiriji_list[nest_i] if len(kiriji_list) > 1 else kiriji_list[0]
            xml_article = etree.SubElement(root, "article")
            export_count += 1
            parse_title(kana, hyouki, kiriji, corpus, number, xml_article)
            parse_rubrics(rubrics, xml_article)
    elif kana_nesting > 0 and hyouki_nesting == 0:
        kana_list = kanas.split(", ")
        kiriji_list = kirijies.split(", ")
        for nest_i in range(kana_nesting + 1):
            kana = kana_list[nest_i]
            hyouki = hyoukies
            kiriji = kiriji_list[nest_i] if len(kiriji_list) > 1 else kiriji_list[0]
            xml_article = etree.SubElement(root, "article")
            export_count += 1
            parse_title(kana, hyouki, kiriji, corpus, number, xml_article)
            parse_rubrics(rubrics, xml_article)
    elif kana_nesting > 0:
        raise RuntimeError("kana nesting process failed")
    else:
        xml_article = etree.SubElement(root, "article")
        export_count += 1
        parse_title(kanas, hyoukies, kirijies, corpus, number, xml_article)
        parse_rubrics(rubrics, xml_article)


def parse_title(kana, hyoukies, kiriji, corpus, number, article_element):
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
                    litter_match = re.match(r'(<i>)(?P<litter>[ёЁа-яА-Я ]*\.):?(</i>)', litter)
                meaning_with_litter_m = re.search(
                    r'((<i>)(?P<corpus>[ёЁа-яА-Я;. ]*)(</i>))?((?P<deri>: ～[一-龯ぁ-んァ-ン]*)|(?P<kanji>[一-龯ぁ-んァ-ン]*))?(?P<comma>: )?(?P<meaning>.*)$',
                    meaning)
                if litter_match is not None and meaning_with_litter_m is not None:
                    # print(litter_kanji)
                    # print(meaning_with_litter_m.groups())
                    meaning = construct_meaning(meaning_with_litter_m, litter_match, litter_kanji)
                elif litter is not None:
                    meaning = litter + " " + meaning
                elif len(litter_kanji) > 0 and meaning_with_litter_m is not None:
                    meaning = meaning_with_litter_m.expand(r"\g<deri> ") + litter_kanji + " " \
                              + meaning_with_litter_m.expand(r"\g<1> \g<meaning>").strip()
                    meaning = meaning.strip()
                else:
                    raise RuntimeError("litter process failed")

            rubric_element.set("translation", meaning)
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
                rubric_element.set("translation", text)
                continue

        if derivative_match is not None:
            derivative_element = etree.SubElement(rubric_element, "derivative")
            derivative_element.text = text
            continue

        if idiom_match is not None:
            idiom_element = etree.SubElement(rubric_element, "idiom")
            idiom_element.text = text
            continue

        phrase_element = etree.SubElement(rubric_element, "phrase")
        phrase_element.text = text


def construct_meaning(meaning_with_litter_m, litter_m, litter_kanji):
    meaning_litter = meaning_with_litter_m.expand(r"\g<corpus>")
    litter = litter_m.expand(r"\g<1>")
    litter += litter_m.expand(r"\g<litter>")
    if len(meaning_litter) > 0:
        litter += " " + meaning_litter
    litter += meaning_with_litter_m.expand(r"\g<comma>").strip()
    litter += litter_m.expand(r"\g<3>")
    return " ".join(filter(lambda x: len(x) > 0,
                           [meaning_with_litter_m.expand(r"\g<deri>"),
                            litter_kanji,
                            litter,
                            meaning_with_litter_m.expand(r"\g<kanji>"),
                            meaning_with_litter_m.expand(r"\g<meaning>").strip()
                            ]
                           ))


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
    return homogram_m.expand(r"\g<1>\g<3>").strip()


def test_parse():
    test_root = etree.Element("warodai")
    files = [
        "004-23-67",
        "006-79-94",
        "005-75-60",
        "008-56-59",
        "007-58-00",
        "002-52-52",
        "005-78-01",
        "004-94-80",
        "006-07-86",
        "007-61-80",
        "009-26-70",
        "007-66-47",
        "007-65-61",
        "009-12-37"
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
