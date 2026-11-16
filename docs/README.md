# 文件索引

[回到專案首頁](../README.md) · [English overview](README.en.md)

| 文件 | 用途 |
|---|---|
| [裝配與試印](assembly.md) | 舵機與舵盤配合條件、試片、列印設定、五金與裝配順序 |
| [模型與列印清單](../output/README.md) | 各 STL 的數量、修改件 STEP、試裝檔案和命名方式 |
| [重建與交付](build.md) | 安裝相依套件、按順序執行腳本、產生 ZIP 與校驗值 |
| [驗證報告](validation.md) | 每個 JSON 報告的用途、已檢查內容與實物待驗證事項 |
| [中文 PDF 指南](../output/裝配與試印指南.pdf) | 六頁圖文版裝配與試印說明 |
| [五金 BOM](../BOM.csv) | 舵機、金屬舵盤、螺絲、螺母及墊片的採購起點 |
| [版本紀錄](../CHANGELOG.md) | R1、R2 及 repo 整理內容 |
| [R1 基準說明](../reference/README.md) | 幾何保留與齒輪回程比對的依據 |

## 目錄分工

- `output/` 放目前 R2 的交付模型與對應檢查結果；STL 用於切片，STEP 用於 CAD 檢視。
- `scripts/` 與 `parameters.json` 用於重建。修改設計後需重新執行相應驗證。
- `upstream/` 保留原專案檔案，來源由 `source_manifest.json` 固定。
- `reference/` 保存比對用的 R1 資料，供 `verify_revision.py` 及齒輪對比圖使用。
- `dist/` 與 `work/` 是本機產物，不納入版本控制。

詳細裝配內容集中在 [assembly.md](assembly.md)。根目錄的 `README_繁體中文.md` 保留為舊連結入口。
