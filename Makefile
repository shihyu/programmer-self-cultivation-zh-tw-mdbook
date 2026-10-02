.DEFAULT_GOAL := help
export PYTHONDONTWRITEBYTECODE := 1

PORT ?= 3000

.PHONY: help build run test publish clean

help:
	@echo "make build  - 轉換 EPUB 並建立離線 HTML 電子書"
	@echo "make run    - 在 http://127.0.0.1:$(PORT) 預覽"
	@echo "make test   - 執行全部單元與系統測試"
	@echo "make publish - 建置、測試並推送 HTML 至 gh-pages"
	@echo "make clean  - 移除可重建的產物"

build:
	@python3 scripts/convert.py
	@python3 scripts/convert.py --check
	@mdbook build
	@cp theme/searcher.js book/searcher.js

run: build
	@lsof -ti:$(PORT) | xargs -r kill -9 2>/dev/null || true
	@mdbook serve -n 127.0.0.1 -p $(PORT)

test:
	@./test.sh

publish: test
	@python3 scripts/publish_pages.py

clean:
	@rm -rf book src/chapters src/images
	@rm -f src/SUMMARY.md src/index.md reports/terminology-review.md
