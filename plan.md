# 《程序員的自我修養》繁體台灣術語 mdBook 計畫

## 任務目標

將使用者提供的 EPUB 製成可離線閱讀的獨立 mdBook HTML 電子書。依 EPUB 的 OPF 閱讀順序保留全文、程式碼、圖表、圖片及章節層級；將正文校成繁體中文與台灣常用資訊術語。原書名與作者資訊保留於來源註記，網站顯示名稱可用台灣用語。參考 `/home/shihyu/github/jason_note` 的 mdBook 設定與導覽習慣，不修改該專案。

## 專案資料夾

`/home/shihyu/下載/programmer-self-cultivation-zh-tw-mdbook/`（kebab-case，表示本書繁體台灣版 mdBook）。來源為同層的 `程序員的自我修養：鏈接、裝載與庫 (俞甲子,石凡,潘愛民).epub`；專案內保留一份原始 EPUB，使日後可重建。

## 範圍與處理原則

- EPUB 目前有 104 個 HTML/XHTML 內容檔、176 張 JPG、1 個 CSS；以 OPF spine 為章節順序，不按檔名字母排序。
- 轉成 `src/*.md` 與 `src/images/`；建立 `src/SUMMARY.md`、`src/index.md` 和 `book.toml`。圖片、章節連結及標題須能在 HTML 中使用。
- 先用 OpenCC 的台灣繁體設定處理文字節點，再以可審查的術語表修正上下文。例：`程序`→`程式`、`鏈接`→`連結`、`裝載`→`載入`、`內存`→`記憶體`、`硬件`→`硬體`、`目標文件`→`目的檔`；實際替換須依技術語境確認，保留 ELF、ABI、API 等識別字。
- 程式碼、命令、檔名、路徑、URL、標籤屬性及數字不做文字轉換。來源中疑似 OCR 錯字與無法確定的術語列入檢查報告，不臆測修正。
- 不新增原書沒有的技術內容；來源文字的改寫應可由術語表或檢查報告追溯。

## 預期產出

```text
programmer-self-cultivation-zh-tw-mdbook/
├── plan.md
├── _doc/v0.1.md
├── book.toml
├── Makefile
├── test.sh
├── source/original.epub
├── scripts/convert.py
├── scripts/terms.json
├── src/SUMMARY.md
├── src/index.md
├── src/chapters/*.md
├── src/images/*.jpg
├── tests/unit/test_conversion.py
├── tests/system/test_book.py
└── book/                  # make build 產生；make clean 清除
```

`source/original.epub`、轉換後章節、圖片、術語表及 `_doc/v0.1.md` 為交付資料；`book/` 是可離線開啟的 HTML 成品。測試過程產生的 log、tmp、fixtures、snapshot 一律放在 `tests/` 並於完成後清理。

## 建置、執行、除錯與測試

- 依賴：現有 `mdbook`、Python 3、OpenCC、BeautifulSoup/lxml；若使用 Markdown 轉換套件，在程式與文件中固定版本或明確列出需求。
- `make`：顯示 help；`make build`：執行轉換、檢查、`mdbook build`；`make run`：先清理預設 `PORT=3000` 的佔用，再以 `mdbook serve -n 127.0.0.1 -p $(PORT)` 啟動；`make test`：呼叫 `./test.sh`；`make clean`：移除生成的 `book/` 與可重建的中間產物。
- `make clean && make build` 須可重複執行。Makefile 以 `.DEFAULT_GOAL := help` 開始；server 的 `run` 命令含 `@lsof -ti:$(PORT) | xargs -r kill -9 2>/dev/null || true`。
- 除錯：`python3 scripts/convert.py --check` 檢查章節、圖片、術語；`mdbook build -v` 檢查 HTML 產出；必要時直接用瀏覽器開啟 `book/index.html`。
- `./test.sh` 為本地與 CI 的唯一全測試入口，執行 `python3 -m unittest discover -s tests/unit`、`python3 -m unittest discover -s tests/system`，以及 `mdbook build`/連結完整性檢查；任何失敗回傳非零。

## 驗收標準

1. 104 個來源內容檔皆出現在 mdBook 導覽中，順序與 OPF spine 一致；正文、程式碼、表格及圖片不遺漏。
2. 176 張來源圖片均有對應檔案，所有本地圖片連結可解析；HTML 可離線開啟，側欄導覽與搜尋可用。
3. 台灣用語的預定術語表全書檢查通過；程式碼與技術識別字不被轉換；另交付未確定用語／疑似 OCR 問題的檢查報告。
4. `make` 顯示 help；`make clean && make build` 可重複；`make test` 與 `./test.sh` 均通過，且測試輸出完整回報。
5. 單元測試覆蓋轉換公開函式與邊界情況；系統測試以讀者角度驗證章節順序、圖片、HTML 建置及離線入口。兩層均不可略過。

## 子任務與 TDD 次序

1. 確認 EPUB 結構、章節序、HTML 元素及術語樣本；完成 `_doc/v0.1.md` 快照。
2. 先寫轉換函式單元測試並實際執行，完整回報失敗輸出；再寫最小實作與術語表，重跑並完整回報。測試失敗時先報告原因並等待討論，不逕自改實作。
3. 先寫整書系統測試並實際執行，完整回報；再產生 Markdown、圖片、SUMMARY、book.toml、Makefile 與 test.sh，重跑並完整回報。
4. 建置並抽查首頁、章節、程式碼、表格、圖片和術語；輸出檢查報告。每一步完成後總結結果與 plan.md 是否需要建議變更。

若執行期間發現需要更改此計畫，只提出變更建議，由使用者確認後修改。
