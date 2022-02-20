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
    parse_article(article_name, article, test_root)
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
            self.assertEqual("блаженство в нирване", rubrics[0].attrib["translation"])

    def test_rubric2(self):
        root = test_parse("005-95-09").getroot()
        for article in root:
            rubrics = article.findall('rubric')
            self.assertEqual("<i>см.</i> <a href=\"#008-98-82\">きめこみにんぎょう</a>", rubrics[0].attrib["translation"])

    # あいだ【間】(айда)〔006-49-94〕
    def test_rubric3(self):
        root = test_parse("006-49-94").getroot()
        self.assertEqual("промежуток, расстояние; интервал", root[0].findall('rubric')[0].attrib["translation"])
        self.assertEqual("1", root[0].findall('rubric')[0].attrib["group"])
        self.assertEqual("<i>связ.</i> период времени", root[0].findall('rubric')[1].attrib["translation"])


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
        self.assertEqual("<i>ист.</i>", root[0].findall('clarification')[0].text)
        self.assertEqual("императорский двор", root[0].findall('rubric')[0].attrib["translation"])
        self.assertEqual("сёгун", root[0].findall('rubric')[1].attrib["translation"])

    # ふでまめ【筆まめ】(фудэмамэ)〔008-56-59〕
    # <i>уст.</i> 筆忠実
    # 1): ～な хорошо владеющий пером;
    # ～である хорошо владеть пером; писать с лёгкостью;
    # 2): ～な любящий писать <i>(письма)</i>.
    def test_litter3(self):
        root = test_parse("008-56-59").getroot()
        self.assertEqual("<i>уст.</i> 筆忠実", root[0].findall('clarification')[0].text)
        self.assertEqual(": ～な хорошо владеющий пером", root[0].findall('rubric')[0].attrib["translation"])
        self.assertEqual("～である хорошо владеть пером; писать с лёгкостью",
                         root[0].findall('rubric')[0].findall('derivative')[0].text)
        self.assertEqual(": ～な любящий писать <i>(письма)</i>", root[0].findall('rubric')[1].attrib["translation"])

    # ぐんけい【軍警】(гункэй)〔005-57-66〕
    # (<i>сокр.</i> 軍事警察)
    # 1) военная полиция; жандармерия;
    # 2) военный полицейский; жандарм.
    def test_litter4(self):
        root = test_parse("005-57-66").getroot()
        self.assertEqual("(<i>сокр.</i> 軍事警察)", root[0].findall('clarification')[0].text)
        self.assertEqual("военная полиция; жандармерия", root[0].findall('rubric')[0].attrib["translation"])
        self.assertEqual("военный полицейский; жандарм", root[0].findall('rubric')[1].attrib["translation"])

    # けいえん【敬遠】(кэйэн)〔007-58-00〕
    #: ～する
    # 1) с почётом удалять (отстранять) <i>кого-л.</i>;
    # 2) держаться почтительно, но на расстоянии; относиться с уважением, но холодно.
    def test_litter7(self):
        root = test_parse("007-58-00").getroot()
        self.assertEqual(": ～する", root[0].findall('clarification')[0].text)
        self.assertEqual("с почётом удалять (отстранять) <i>кого-л.</i>",
                         root[0].findall('rubric')[0].attrib["translation"])
        self.assertEqual("держаться почтительно, но на расстоянии; относиться с уважением, но холодно",
                         root[0].findall('rubric')[1].attrib["translation"])

    # そう【添う】(соу)〔002-52-52〕
    # (に)
    # 1) сопровождать <i>кого-л.</i>; следовать <i>за чем-л.</i>;
    # 影の形に添うように как тень <i>(идти за кем-л.)</i>;
    # 2) вступать в брак, жениться, выходить замуж;
    # …と添われるようにと祈る мечтать жениться на <i>ком-л.</i> (выйти замуж за <i>кого-л.</i>);
    # 添われぬ縁とあきらめてくれ оставь надежду жениться на мне.
    def test_litter8(self):
        root = test_parse("002-52-52").getroot()
        self.assertEqual("(に)", root[0].findall('clarification')[0].text)
        self.assertEqual("сопровождать <i>кого-л.</i>; следовать <i>за чем-л.</i>",
                         root[0].findall('rubric')[0].attrib["translation"])
        self.assertEqual("вступать в брак, жениться, выходить замуж",
                         root[0].findall('rubric')[1].attrib["translation"])

    def test_litter9(self):
        root = test_parse("005-78-01").getroot()
        self.assertEqual("(<i>нем.</i> Aphtha[e]) <i>мед.</i>", root[0].findall('clarification')[0].text)
        self.assertEqual("молочница", root[0].findall('rubric')[0].attrib["translation"])
        self.assertEqual("афты", root[0].findall('rubric')[1].attrib["translation"])

    # ふじゅん【不純】(фудзюн)〔004-94-80〕
    # : ～な <i>прям. и перен.</i>
    # 1) нечистый, грязный;
    # 2) смешанный, разбавленный.
    def test_litter10(self):
        root = test_parse("004-94-80").getroot()
        self.assertEqual(": ～な <i>прям. и перен.</i>", root[0].findall('clarification')[0].text)
        self.assertEqual("нечистый, грязный", root[0].findall('rubric')[0].attrib["translation"])
        self.assertEqual("смешанный, разбавленный", root[0].findall('rubric')[1].attrib["translation"])

    # …かさね【…重ね】(…касанэ)〔006-07-86〕
    # <i>уст.</i> 襲ね
    # <i>счётный суф.:</i>
    # 1) <i>для костюмов и различных комплектов</i>;
    # <...>
    # 2) <i>для слоёв; для полок и т. п.</i>;
    def test_litter11(self):
        root = test_parse("006-07-86").getroot()
        self.assertEqual("<i>уст.</i> 襲ね", root[0].findall('clarification')[0].text)
        self.assertEqual("<i>счётный суф.:</i>", root[0].findall('clarification')[1].text)
        self.assertEqual("<i>для костюмов и различных комплектов</i>",
                         root[0].findall('rubric')[0].attrib["translation"])
        self.assertEqual("<i>для слоёв; для полок и т. п.</i>", root[0].findall('rubric')[1].attrib["translation"])

    # けんぱい【献杯･献盃】(кэмпай)〔008-33-61〕
    # 1) (<i>тж.</i> 勧盃)
    #: ～する угощать вином <i>кого-л.</i>, предлагать бокал вина <i>кому-л.</i>;
    # <...>
    def test_litter12(self):
        root = test_parse("008-33-61").getroot()
        self.assertEqual("(<i>тж.</i> 勧盃)", root[0].findall('rubric')[0].attrib["clarification"])
        self.assertEqual(": ～する угощать вином <i>кого-л.</i>, предлагать бокал вина <i>кому-л.</i>",
                         root[0].findall('rubric')[0].findall('derivative')[0].text)
        self.assertEqual("<i>см.</i> <a href=\"#008-19-10\">かんぱい【乾杯】</a>",
                         root[0].findall('rubric')[1].attrib["references"])


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
