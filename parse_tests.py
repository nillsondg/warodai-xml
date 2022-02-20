import os
import unittest
from lxml import etree

from main import warodai_dir, read_article, parse_article


def test_parse(filename):
    test_root = etree.Element("warodai")
    numbers = filename.split("-")
    file = f"{warodai_dir}/{numbers[0]}/{numbers[1]}/{filename}.txt"
    article_name = os.path.basename(file).split(".")[0]
    article = read_article(file)
    parse_article(article_name, article, test_root, 0)
    return etree.ElementTree(test_root)


class HyoukiesTestCase(unittest.TestCase):

    def test_hyouki1(self):
        root = test_parse("004-99-20").getroot()
        for article in root:
            hyoukies = article.findall('hyouki')
            self.assertEqual("処々", hyoukies[0].text)
            self.assertEqual("所々", hyoukies[1].text)
            self.assertEqual("諸所", hyoukies[2].text)
            self.assertEqual("処処", hyoukies[3].text)
            self.assertEqual("所所", hyoukies[4].text)

    def test_hyouki2(self):
        root = test_parse("008-11-96").getroot()
        for article in root:
            hyoukies = article.findall('hyouki')
            self.assertEqual("痺れ鱏", hyoukies[0].text)
            self.assertEqual("痺れ鱝", hyoukies[1].text)

    # гнездование
    # エッキスせん, エッキスこうせん【X線, X光線】(эккйсўсэн, эккйсўко:сэн)〔002-99-75〕
    # def test_hyouki3(self):
    #     root = test_parse("002-99-75").getroot()
    #     for article in root:
    #         hyoukies = article.findall('hyouki')
    #         self.assertEqual("X線", hyoukies[0].text)
    #         self.assertEqual("X光線", hyoukies[1].text)


class KanaTestsCase(unittest.TestCase):
    def test_kana1(self):
        root = test_parse("005-01-17").getroot()
        for article in root:
            kana = article.attrib['kana']
            self.assertEqual("ピッチ", kana)


class RubricsTestCase(unittest.TestCase):
    def test_rubric1(self):
        root = test_parse("007-66-47").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual("блаженство в нирване", rubrics[0][0].text)

    def test_rubric2(self):
        root = test_parse("005-95-09").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual("<i>см.</i> <a href=\"#008-98-82\">きめこみにんぎょう</a>", rubrics[0][0].text)


class HomogramsTestCase(unittest.TestCase):

    # todo несостыковочка в документации
    # ああ, あゝI (а:)〔000-95-65〕
    def test_homogram1(self):
        root = test_parse("000-95-65").getroot()
        self.assertEqual("ああ", root[0].attrib['kana'])
        self.assertEqual("あゝ", root[1].attrib['kana'])
        self.assertEqual("а:", root[0].attrib['kiriji'])

    def test_homogram2(self):
        root = test_parse("009-07-76").getroot()
        for article in root:
            hyoukies = article.findall('hyouki')
            self.assertEqual("青大将", hyoukies[0].text)
            self.assertEqual("黄頷蛇", hyoukies[1].text)

    def test_homogram3(self):
        root = test_parse("006-19-66").getroot()
        for article in root:
            hyoukies = article.findall('hyouki')
            self.assertEqual("青大将", hyoukies[0].text)

    def test_homogram4(self):
        root = test_parse("001-34-95").getroot()
        for article in root:
            hyoukies = article.findall('hyouki')
            self.assertEqual("ICBM", hyoukies[0].text)
            self.assertEqual("I.C.B.M.", hyoukies[1].text)


class LittersTestCase(unittest.TestCase):

    # пометы
    def test_litter1(self):
        root = test_parse("004-23-67").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual("<i>ист.</i> императорский двор", rubrics[0][0].text)
            self.assertEqual("<i>ист.</i> сёгун", rubrics[1][0].text)

    # пометы
    def test_litter2(self):
        root = test_parse("006-79-94").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual("<i>уст.</i> носильщик паланкина", rubrics[0][0].text)
            self.assertEqual("<i>уст. перен. прост.</i> ловкач, продувной парень", rubrics[1][0].text)

    def test_litter3(self):
        root = test_parse("008-56-59").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual(": ～な (<i>уст.</i> 筆忠実) хорошо владеющий пером", rubrics[0][0].text)
            self.assertEqual(": ～な (<i>уст.</i> 筆忠実) любящий писать <i>(письма)</i>", rubrics[1][0].text)

    def test_litter4(self):
        root = test_parse("005-57-66").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual("(<i>сокр.</i> 軍事警察) военная полиция; жандармерия", rubrics[0][0].text)
            self.assertEqual("(<i>сокр.</i> 軍事警察) военный полицейский; жандарм", rubrics[1][0].text)

    def test_litter5(self):
        root = test_parse("001-95-90").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual("(<i>русск.</i> народники) народники", rubrics[0][0].text)
            self.assertEqual("(<i>русск.</i> народники) народничество", rubrics[1][0].text)

    def test_litter6(self):
        root = test_parse("005-75-60").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual("<i>ономат.:</i> かんかん鳴る звенеть; лязгать", rubrics[0][0].text)
            self.assertEqual("<i>ономат.:</i> かんかん日が照っている солнце светит ярко", rubrics[1][0].text)
            self.assertEqual("<i>ономат.:</i> かんかんに怒る вспыхнуть от гнева, загореться гневом", rubrics[2][0].text)

    def test_litter7(self):
        root = test_parse("007-58-00").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual(": ～する с почётом удалять (отстранять) <i>кого-л.</i>", rubrics[0][0].text)
            self.assertEqual(": ～する держаться почтительно, но на расстоянии; относиться с уважением, но холодно",
                             rubrics[1][0].text)

    def test_litter8(self):
        root = test_parse("002-52-52").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual("(に) сопровождать <i>кого-л.</i>; следовать <i>за чем-л.</i>", rubrics[0][0].text)
            self.assertEqual("(に) вступать в брак, жениться, выходить замуж", rubrics[1][0].text)

    def test_litter9(self):
        root = test_parse("005-78-01").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual("(<i>нем.</i> Aphtha[e]) <i>мед.</i> молочница", rubrics[0][0].text)
            self.assertEqual("(<i>нем.</i> Aphtha[e]) <i>мед.</i> афты", rubrics[1][0].text)

    def test_litter10(self):
        root = test_parse("004-94-80").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual(": ～な <i>прям. и перен.</i> нечистый, грязный", rubrics[0][0].text)
            self.assertEqual(": ～な <i>прям. и перен.</i> смешанный, разбавленный", rubrics[1][0].text)

    def test_litter11(self):
        root = test_parse("006-07-86").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual("(<i>уст.</i> 襲ね) <i>счётный суф. для костюмов и различных комплектов</i>",
                             rubrics[0][0].text)
            self.assertEqual("(<i>уст.</i> 襲ね) <i>счётный суф. для слоёв; для полок и т. п.</i>", rubrics[1][0].text)


class NestingTestsCase(unittest.TestCase):

    # ちょうへん, ちょうへんしょうせつ【長篇･長編, 長篇小説･長編小説】(тё:хэн, тё:хэн-сё:сэцу)〔009-26-70〕
    def test_nesting1(self):
        root = test_parse("009-26-70").getroot()
        self.assertEqual("ちょうへん", root[0].attrib['kana'])
        self.assertEqual("ちょうへんしょうせつ", root[1].attrib['kana'])
        self.assertEqual("тё:хэн", root[0].attrib['kiriji'])
        self.assertEqual("тё:хэн-сё:сэцу", root[1].attrib['kiriji'])
        hyoukies = root[0].findall('hyouki')
        self.assertEqual("長篇", hyoukies[0].text)
        self.assertEqual("長編", hyoukies[1].text)
        hyoukies = root[1].findall('hyouki')
        self.assertEqual("長篇小説", hyoukies[0].text)
        self.assertEqual("長編小説", hyoukies[1].text)

    # ちりぢり, ちりぢりばらばら【散々, 散々ばらばら】(тиридзири, тиридзири-барабара)〔005-50-45〕
    def test_nesting2(self):
        root = test_parse("005-50-45").getroot()
        self.assertEqual("ちりぢり", root[0].attrib['kana'])
        self.assertEqual("ちりぢりばらばら", root[1].attrib['kana'])
        self.assertEqual("тиридзири", root[0].attrib['kiriji'])
        self.assertEqual("тиридзири-барабара", root[1].attrib['kiriji'])
        self.assertEqual("散々", root[0].findall('hyouki')[0].text)
        self.assertEqual("散々ばらばら", root[1].findall('hyouki')[0].text)

    # あいそ, あいそう【愛想】(айсо, айсо:)〔009-12-37〕
    def test_nesting3(self):
        root = test_parse("009-12-37").getroot()
        self.assertEqual("あいそ", root[0].attrib['kana'])
        self.assertEqual("あいそう", root[1].attrib['kana'])
        self.assertEqual("айсо", root[0].attrib['kiriji'])
        self.assertEqual("айсо:", root[1].attrib['kiriji'])
        self.assertEqual("愛想", root[0].findall('hyouki')[0].text)
        self.assertEqual("愛想", root[1].findall('hyouki')[0].text)

    # てんでに, てんでんに(тэндэни, тэндэнни)〔000-16-88〕
    def test_nesting4(self):
        root = test_parse("000-16-88").getroot()
        self.assertEqual("てんでに", root[0].attrib['kana'])
        self.assertEqual("てんでんに", root[1].attrib['kana'])
        self.assertEqual("тэндэни", root[0].attrib['kiriji'])
        self.assertEqual("тэндэнни", root[1].attrib['kiriji'])

    # ターボジェットき【ターボジェット機】(та:бодзеттоки, та:бодзйеттоки)〔008-07-89〕
    def test_nesting5(self):
        root = test_parse("008-07-89").getroot()
        self.assertEqual("ターボジェットき", root[0].attrib['kana'])
        self.assertEqual("та:бодзеттоки, та:бодзйеттоки", root[0].attrib['kiriji'])
        self.assertEqual("ターボジェット機", root[0].findall('hyouki')[0].text)

    # です(дэс, дэсў)〔006-48-38〕
    def test_nesting6(self):
        root = test_parse("006-48-38").getroot()
        self.assertEqual("です", root[0].attrib['kana'])
        self.assertEqual("дэс, дэсў", root[0].attrib['kiriji'])

    # ボロ・タク, ぼろ・タク(боро-таку)〔007-29-08〕
    def test_nesting7(self):
        root = test_parse("007-29-08").getroot()
        self.assertEqual("ボロ・タク", root[0].attrib['kana'])
        self.assertEqual("ぼろ・タク", root[1].attrib['kana'])
        self.assertEqual("боро-таку", root[0].attrib['kiriji'])
        self.assertEqual("боро-таку", root[1].attrib['kiriji'])


if __name__ == '__main__':
    unittest.main()
