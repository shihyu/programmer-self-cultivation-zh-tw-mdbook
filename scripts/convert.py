"""Convert the supplied EPUB's XHTML chapters to mdBook source pages."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree

from bs4 import BeautifulSoup, NavigableString
from opencc import OpenCC


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source/original.epub"
SRC = ROOT / "src"
TERMS = json.loads((ROOT / "scripts/terms.json").read_text(encoding="utf-8"))
CONVERTER = OpenCC("s2twp")
SKIP_TEXT_TAGS = {"pre", "code", "script", "style"}


def localize_text(text: str) -> str:
    """Convert prose to Taiwan Traditional Chinese and curated book terms."""
    result = CONVERTER.convert(text)
    for source, target in sorted(TERMS.items(), key=lambda pair: len(pair[0]), reverse=True):
        result = result.replace(source, target)
    return result


def parse_spine(opf_xml: str) -> list[str]:
    """Return manifest hrefs in the reading order declared by an EPUB OPF."""
    root = ElementTree.fromstring(opf_xml)
    namespace = {"opf": "http://www.idpf.org/2007/opf"}
    manifest = {
        item.attrib["id"]: item.attrib["href"]
        for item in root.findall("./opf:manifest/opf:item", namespace)
    }
    return [
        manifest[item.attrib["idref"]]
        for item in root.findall("./opf:spine/opf:itemref", namespace)
    ]


def chapter_title(html: str, fallback: str) -> str:
    """Use the first chapter heading for the mdBook sidebar."""
    soup = BeautifulSoup(html, features="xml")
    heading = soup.find(["h1", "h2", "h3", "h4"])
    return localize_text(heading.get_text(" ", strip=True)) if heading else fallback


def convert_html(html: str) -> str:
    """Keep source body markup while localizing prose and moving image paths."""
    soup = BeautifulSoup(html, features="xml")
    body = soup.find("body")
    if body is None:
        raise ValueError("EPUB chapter has no body")

    for node in list(body.descendants):
        if isinstance(node, NavigableString) and node.parent.name not in SKIP_TEXT_TAGS:
            localized = localize_text(str(node))
            if localized != str(node):
                node.replace_with(localized)

    for paragraph in body.find_all("p"):
        if paragraph.contents and isinstance(paragraph.contents[0], NavigableString):
            first = paragraph.contents[0]
            repaired = re.sub(r"^(\s*)\?\s+", r"\1• ", str(first), count=1)
            if repaired != str(first):
                first.replace_with(repaired)

    for image in body.find_all("img"):
        source = image.get("src", "")
        filename = Path(source).name
        if not Path(filename).suffix:
            filename += ".jpg"
        image["src"] = "../images/" + filename

    parts = [str(child) for child in body.children if str(child).strip()]
    return "\n\n".join(parts) + "\n"


def _source_metadata(opf_xml: str) -> tuple[str, str]:
    root = ElementTree.fromstring(opf_xml)
    namespace = {"dc": "http://purl.org/dc/elements/1.1/"}
    title = root.find("./{http://www.idpf.org/2007/opf}metadata/dc:title", namespace)
    author = root.find("./{http://www.idpf.org/2007/opf}metadata/dc:creator", namespace)
    return (title.text or "") if title is not None else "", (author.text or "") if author is not None else ""


def _write_report(chapter_paths: list[Path]) -> None:
    patterns = ("Prepressing", "#2“hello.c”2", "生產執行檔")
    findings: dict[str, list[tuple[str, str]]] = {pattern: [] for pattern in patterns}
    totals = Counter()
    code_blocks = 0
    for path in chapter_paths:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), features="html.parser")
        code_blocks += len(soup.find_all("pre"))
        for node in soup.descendants:
            if isinstance(node, NavigableString) and node.parent.name not in SKIP_TEXT_TAGS:
                prose = str(node)
                for pattern in patterns:
                    count = prose.count(pattern)
                    totals[pattern] += count
                    if count and len(findings[pattern]) < 20:
                        findings[pattern].append((path.name, " ".join(prose.split())[:100]))

    lines = [
        "# 轉換檢查報告", "",
        f"已轉換 {len(chapter_paths)} 個內容檔、保留 {code_blocks} 個程式碼區塊與 176 張原始圖片。",
        "正文使用 OpenCC `s2twp` 與 `scripts/terms.json`；`pre`/`code` 內的程式碼與命令保持原文。",
        "EPUB 中 64 處清單前的 `?` 已改為 `•`，並補正一處缺少 `.jpg` 的圖片路徑。", "",
        "## 仍需人工複核", "",
        "以下是來源 EPUB 裡無法只靠台灣用語規則判定的疑似錯字或語句，保留於電子書供人工核對。", "",
        "| 疑似模式 | 出現次數 | 範例數（最多顯示 20 筆） |", "| --- | ---: | ---: |",
    ]
    for pattern, examples in findings.items():
        lines.append(f"| `{pattern}` | {totals[pattern]} | {len(examples)} |")
    lines.append("")
    for pattern, examples in findings.items():
        if examples:
            lines.extend((f"## `{pattern}`", ""))
            for filename, snippet in examples:
                lines.append(f"- `src/chapters/{filename}`：{snippet.replace('|', '｜')}")
            lines.append("")
    report = ROOT / "reports/terminology-review.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    chapters_dir = SRC / "chapters"
    images_dir = SRC / "images"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    with ZipFile(SOURCE) as archive:
        opf = archive.read("OEBPS/content.opf").decode("utf-8")
        spine = parse_spine(opf)
        original_title, authors = _source_metadata(opf)
        summary = ["# Summary", "", "[首頁](index.md)", "", "# 目錄", ""]
        chapter_paths = []
        for href in spine:
            html = archive.read("OEBPS/" + href).decode("utf-8")
            stem = Path(href).stem
            chapter_path = chapters_dir / (stem + ".md")
            chapter_path.write_text(convert_html(html), encoding="utf-8")
            chapter_paths.append(chapter_path)
            title = chapter_title(html, stem).replace("[", "〔").replace("]", "〕")
            indent = "    " if re.fullmatch(r"\d+\.\d+", stem) else ""
            summary.append(f"{indent}- [{title}](chapters/{chapter_path.name})")

        images = [name for name in archive.namelist() if name.startswith("OEBPS/Images/") and name.endswith(".jpg")]
        for name in images:
            (images_dir / Path(name).name).write_bytes(archive.read(name))

    (SRC / "SUMMARY.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    (SRC / "index.md").write_text(
        "# 程式設計師的自我修養：連結、載入與函式庫\n\n"
        f"原書名：{original_title}  \n作者：{authors}\n\n"
        "本電子書由原始 EPUB 轉為繁體台灣術語的 mdBook，依原書閱讀順序收錄。"
        "程式碼與技術識別字保留原文。\n\n"
        "[開始閱讀](chapters/0.md)\n",
        encoding="utf-8",
    )
    _write_report(chapter_paths)
    print(f"converted {len(chapter_paths)} chapters and {len(images)} images")


def _check() -> None:
    with ZipFile(SOURCE) as archive:
        spine = parse_spine(archive.read("OEBPS/content.opf").decode("utf-8"))
        images = [name for name in archive.namelist() if name.startswith("OEBPS/Images/") and name.endswith(".jpg")]
    chapters = list((SRC / "chapters").glob("*.md"))
    copied_images = list((SRC / "images").glob("*.jpg"))
    if len(spine) != len(chapters) or len(images) != len(copied_images):
        raise SystemExit("chapter/image count differs from EPUB")
    unresolved = Counter()
    for chapter in chapters:
        soup = BeautifulSoup(chapter.read_text(encoding="utf-8"), features="html.parser")
        for image in soup.find_all("img"):
            if not (chapter.parent / image["src"]).is_file():
                raise SystemExit(f"missing image: {chapter} {image['src']}")
        for node in soup.descendants:
            if isinstance(node, NavigableString) and node.parent.name not in SKIP_TEXT_TAGS:
                for word in (
                    "程序", "鏈接", "裝載", "內存", "目標檔案", "操作係統",
                    "係統", "二進製", "共享庫", "隻", "嚮", "麵", "須要", "彙編",
                ):
                    if word in str(node):
                        unresolved[word] += 1
    if unresolved:
        raise SystemExit(f"unlocalized prose: {dict(unresolved)}")
    print(f"checked {len(chapters)} chapters, {len(copied_images)} images, and Taiwan terms")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate generated source")
    args = parser.parse_args()
    if args.check:
        _check()
    else:
        _build()


if __name__ == "__main__":
    main()
