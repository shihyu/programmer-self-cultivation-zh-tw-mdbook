import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

from bs4 import BeautifulSoup, NavigableString


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "source/original.epub"
CHAPTERS = ROOT / "src/chapters"
IMAGES = ROOT / "src/images"
BOOK = ROOT / "book"


class BookTests(unittest.TestCase):
    def test_source_is_self_contained_and_summary_follows_spine(self):
        from scripts.convert import parse_spine

        self.assertTrue(SOURCE.is_file())
        with ZipFile(SOURCE) as archive:
            spine = parse_spine(archive.read("OEBPS/content.opf").decode("utf-8"))
        listed = re.findall(r"\]\(chapters/([^)]+)\)", (ROOT / "src/SUMMARY.md").read_text())
        expected = [Path(href).stem + ".md" for href in spine]
        self.assertEqual(len(expected), 104)
        self.assertEqual(listed, expected)
        self.assertEqual(sorted(p.name for p in CHAPTERS.glob("*.md")), sorted(expected))

    def test_chapters_keep_paragraphs_code_tables_and_images(self):
        from scripts.convert import parse_spine

        with ZipFile(SOURCE) as archive:
            spine = parse_spine(archive.read("OEBPS/content.opf").decode("utf-8"))
            for href in spine:
                with self.subTest(href=href):
                    original = BeautifulSoup(archive.read("OEBPS/" + href), features="xml")
                    generated = BeautifulSoup((CHAPTERS / (Path(href).stem + ".md")).read_text(), features="html.parser")
                    for tag in ("h1", "h2", "p", "span", "pre", "code", "table", "tr", "td", "sup", "img"):
                        self.assertEqual(len(original.find_all(tag)), len(generated.find_all(tag)), tag)
                    for tag in ("pre", "code"):
                        self.assertEqual(
                            [node.get_text() for node in original.find_all(tag)],
                            [node.get_text() for node in generated.find_all(tag)],
                        )

    def test_all_images_are_identical_and_referenced(self):
        with ZipFile(SOURCE) as archive:
            images = [name for name in archive.namelist() if name.startswith("OEBPS/Images/") and name.endswith(".jpg")]
            self.assertEqual(len(images), 176)
            self.assertEqual(len(list(IMAGES.glob("*.jpg"))), 176)
            for name in images:
                with self.subTest(name=name):
                    self.assertEqual((IMAGES / Path(name).name).read_bytes(), archive.read(name))
        for chapter in CHAPTERS.glob("*.md"):
            soup = BeautifulSoup(chapter.read_text(), features="html.parser")
            for image in soup.find_all("img"):
                with self.subTest(chapter=chapter.name, image=image.get("src")):
                    self.assertTrue((chapter.parent / image["src"]).is_file())

    def test_prose_uses_localized_terms_without_changing_code(self):
        forbidden = (
            "程序", "鏈接", "裝載", "內存", "目標檔案", "操作係統",
            "係統", "二進製", "共享庫", "隻", "嚮", "麵", "須要", "彙編",
        )
        chapters = list(CHAPTERS.glob("*.md"))
        self.assertEqual(len(chapters), 104)
        for chapter in chapters:
            soup = BeautifulSoup(chapter.read_text(), features="html.parser")
            for node in soup.descendants:
                if isinstance(node, NavigableString) and node.parent.name not in {"pre", "code"}:
                    for term in forbidden:
                        with self.subTest(chapter=chapter.name, term=term):
                            self.assertNotIn(term, str(node))

    def test_offline_html_and_make_targets_exist(self):
        self.assertTrue((BOOK / "index.html").is_file())
        self.assertTrue((BOOK / "searchindex.js").is_file())
        self.assertEqual(len(list((BOOK / "chapters").glob("*.html"))), 104)
        result = subprocess.run(["make"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for target in ("build", "run", "test", "clean"):
            self.assertIn(target, result.stdout)

    def test_rendered_pages_keep_content_and_local_links(self):
        from scripts.convert import parse_spine

        with ZipFile(SOURCE) as archive:
            spine = parse_spine(archive.read("OEBPS/content.opf").decode("utf-8"))
            for href in spine:
                with self.subTest(href=href):
                    original = BeautifulSoup(archive.read("OEBPS/" + href), features="xml")
                    rendered_path = BOOK / "chapters" / (Path(href).stem + ".html")
                    rendered = BeautifulSoup(rendered_path.read_text(), features="html.parser")
                    content = rendered.select_one("#content")
                    self.assertIsNotNone(content)
                    for tag in ("h1", "h2", "p", "span", "pre", "code", "table", "tr", "td", "sup", "img"):
                        self.assertEqual(len(original.find_all(tag)), len(content.find_all(tag)), tag)

        for page in BOOK.rglob("*.html"):
            soup = BeautifulSoup(page.read_text(), features="html.parser")
            for node in soup.select("a[href], link[href], script[src], img[src]"):
                uri = node.get("href") or node.get("src")
                parsed = urlsplit(uri)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                with self.subTest(page=page.name, uri=uri):
                    target = (page.parent / unquote(parsed.path)).resolve()
                    self.assertTrue(target.is_file(), str(target))

    def test_review_report_records_remaining_source_issues(self):
        report = (ROOT / "reports/terminology-review.md").read_text()
        self.assertIn("Prepressing", report)
        self.assertIn("#2“hello.c”2", report)
        self.assertIn("人工複核", report)

    def test_make_publish_builds_and_tests_before_pushing(self):
        result = subprocess.run(["make", "-n", "publish"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLess(result.stdout.index("./test.sh"), result.stdout.index("scripts/publish_pages.py"))


if __name__ == "__main__":
    unittest.main()
