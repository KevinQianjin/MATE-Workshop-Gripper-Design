# MATE Workshop Gripper Design

可 3D 列印的雙自由度夾爪：**開合＋左右轉向**，目前為 **R2 匹配齒輪試裝版**，暫按兩顆 GDW IPX896HV 舵機設計。

[模型與列印清單](output/README.md) · [裝配說明](docs/assembly.md) · [中文 PDF](output/裝配與試印指南.pdf) · [五金 BOM](BOM.csv) · [English](docs/README.en.md)

![R2 雙自由度夾爪裝配](output/preview/assembly_open.png)

## 從這裡開始

| 你要做什麼 | 開啟檔案 |
|---|---|
| 在 Fusion / SolidWorks 查看整機 | [完整裝配 STEP](output/IPX896HV_2DOF_assembly.step) |
| 先確認舵機、舵盤與齒輪配合 | [試印件](output/fit_checks/)及[試裝步驟](docs/assembly.md#試片流程) |
| 列印完整機構 | [12 種主要零件、14 件列印清單](output/README.md#主要列印件) |
| 調整模型 | [8 個修改／新增零件 STEP](output/step/)及[尺寸參數](parameters.json) |
| 查看齒輪改善與檢查結果 | [齒輪對比圖](output/preview/gear_review_R2.pdf)及[驗證報告索引](docs/validation.md) |
| 重建或打包檔案 | [重建與交付流程](docs/build.md) |

1. 下載 repo（GitHub **Code → Download ZIP** 或 `git clone`），先讀[裝配指南](docs/assembly.md)。使用現有 STEP／STL 不需要安裝 Python。
2. 先印 F01–F04 接口試片，再印 F05 底板及 B12 的 20T、19T 齒輪各兩件，確認配合。
3. 試裝通過後，再依[列印清單](output/README.md)和 [BOM](BOM.csv)準備整機，空載校準可用端點。

## 目前設計

| 項目 | R2 |
|---|---|
| 自由度 | 開合＋左右轉向，共 2 軸 |
| 主要列印件 | 12 種、14 件；`PRINT_2` 檔案印兩件 |
| 齒輪配置 | 模數 0.75、壓力角 20°、20／19／19／20 齒 |
| 相對 R1 的更換範圍 | M01、M02、M05、M06 ×2，共 4 種、5 件 |
| 輸出端幾何回程估算 | 約 2.75°；R1 約 8.2–11.6° |
| CAD 驗證 | 23 個 STL、20 個 STEP、145 個名義齒面位置及 20 個正反向接觸邊界姿態 |

**目前是完成 CAD 檢查的試裝原型。**舵機固定耳、金屬舵盤、實際列印配合及承載能力仍需實測。回程數值為剛體模型估算，未計入打印誤差及舵機自身回程。R2 掌板與齒輪需成套使用；細節見[裝配說明](docs/assembly.md)與[驗證範圍](docs/validation.md)。

## Repo 結構

```text
docs/                 裝配、重建、驗證說明與英文介紹
output/               可直接查看的 R2 模型、試片、PDF 與驗證結果
scripts/              CAD 生成、檢查、繪圖與打包程式
reference/            R1 比對基準
upstream/             原 GitHub 專案檔案與授權
BOM.csv               採購五金清單
parameters.json       設計尺寸與待確認假設
CHANGELOG.md          版本紀錄
source_manifest.json  固定來源版本與檔案雜湊
DELIVERY_SHA256SUMS.txt 交付檔案校驗值
```

`dist/` 是執行打包後產生的交付目錄；`work/` 是本機工作目錄，兩者均不提交到 Git。進一步導覽見[文件索引](docs/README.md)。

## 來源與授權

基於 [vshreyas121-code/6-dof-robotic-arm](https://github.com/vshreyas121-code/6-dof-robotic-arm)，固定版本 `258d1893ba1b8b49e87baa79da462680fd53681b`。原夾指、連桿、輪轂及底座配置盡量沿用，R2 更換工作齒圈。

採用 MIT 授權，見 [LICENSE](LICENSE)、[NOTICE.txt](NOTICE.txt)及[原作者授權](upstream/LICENSE)。版本差異見 [CHANGELOG](CHANGELOG.md)。
