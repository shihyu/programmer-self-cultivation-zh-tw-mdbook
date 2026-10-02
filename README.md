# 程式設計師的自我修養：連結、載入與函式庫

這是從使用者提供的 EPUB 製成的獨立繁體台灣術語 mdBook。原始 EPUB 存在 `source/original.epub`；`src/` 是可重建的書籍來源；`book/index.html` 是可離線開啟的電子書首頁。

## 使用

```bash
make                 # 顯示指令
make build           # 重新產生書籍與離線 HTML
make run             # http://127.0.0.1:3000 預覽
make test            # 執行單元與系統測試
make publish         # 建置、測試並推送 HTML 至 gh-pages
make clean           # 清除可重建產物
```

需要 mdBook 0.4.52 與 Python 3。Python 套件版本見 `requirements.txt`，可用 `python3 -m pip install -r requirements.txt` 安裝。除錯時使用 `RUST_LOG=mdbook=debug mdbook build`；這版 mdBook 不支援 `mdbook build -v`。

轉換器將正文轉為繁體台灣用語，保留 `<pre>` 與 `<code>` 的原文、章節順序及所有原始圖片。來源 EPUB 的疑似 OCR 錯誤與尚待人工複核的語句列在 `reports/terminology-review.md`。

## GitHub Pages

`make publish` 會先透過 `test.sh` 建置並測試，再將 `book/` 的 HTML、CSS、JavaScript 與圖片提交至 `gh-pages` 分支根目錄並推送到 `origin`。該分支含 `.nojekyll`；GitHub Pages 的來源應設為 `gh-pages` / `(root)`。原始檔案留在 `main`，可正常用 `git push origin main` 更新。公開站點為 `https://shihyu.github.io/programmer-self-cultivation-zh-tw-mdbook/`。
