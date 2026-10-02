import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.convert import chapter_title, convert_html, localize_text, parse_spine


class ConversionTests(unittest.TestCase):
    def test_localize_text_uses_taiwan_terms(self):
        text = "程序員分析鏈接、裝載、內存與目標文件。"
        self.assertEqual(
            localize_text(text),
            "程式設計師分析連結、載入、記憶體與目的檔。",
        )

    def test_localize_text_repairs_common_ocr_and_technical_terms(self):
        self.assertEqual(
            localize_text("係統隻須嚮後看，前麵是二進製彙編語言與共享庫。"),
            "系統只需要向後看，前面是二進位組合語言與共用函式庫。",
        )

    def test_convert_html_preserves_code_and_rewrites_image(self):
        html = (
            '<html><body><h2>鏈接</h2><p>程序和裝載</p>'
            '<pre>#include &lt;stdio.h&gt;\n程序</pre>'
            '<p><code>程序</code><img src="../Images/2-1.jpg" alt="圖"/></p>'
            '</body></html>'
        )
        output = convert_html(html)
        self.assertIn("<h2>連結</h2>", output)
        self.assertIn("程式和載入", output)
        self.assertIn("#include &lt;stdio.h&gt;\n程序", output)
        self.assertIn("<code>程序</code>", output)
        self.assertIn('src="../images/2-1.jpg"', output)

    def test_convert_html_repairs_extensionless_jpg_reference(self):
        output = convert_html('<body><p><img src="../Images/7-0-2"/></p></body>')
        self.assertIn('src="../images/7-0-2.jpg"', output)

    def test_convert_html_repairs_epub_bullet_placeholder(self):
        output = convert_html('<body><p>? 將所有巨集展開。</p><p>這是問題？</p></body>')
        self.assertIn('<p>• 將所有巨集展開。</p>', output)
        self.assertIn('<p>這是問題？</p>', output)

    def test_localize_text_repairs_obvious_sentence_error(self):
        self.assertEqual(localize_text('編譯運行通過一氣嗬成'), '編譯、執行一氣呵成')

    def test_localize_text_repairs_remaining_common_variants(self):
        self.assertEqual(
            localize_text('一檯機器每秒鍾處理十六進製資料並與其他機器聯係。'),
            '一台機器每秒鐘處理十六進位資料並與其他機器聯繫。',
        )

    def test_parse_spine_follows_idref_order(self):
        opf = '''<package xmlns="http://www.idpf.org/2007/opf">
          <manifest><item id="b" href="Text/2.html"/>
                    <item id="a" href="Text/1.html"/></manifest>
          <spine><itemref idref="a"/><itemref idref="b"/></spine>
        </package>'''
        self.assertEqual(parse_spine(opf), ["Text/1.html", "Text/2.html"])

    def test_chapter_title_uses_heading_and_fallback(self):
        self.assertEqual(chapter_title("<body><h2>第1章 鏈接</h2></body>", "x"), "第1章 連結")
        self.assertEqual(chapter_title("<body><p>正文</p></body>", "無標題"), "無標題")


if __name__ == "__main__":
    unittest.main()
