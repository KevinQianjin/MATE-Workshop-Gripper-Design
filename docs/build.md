# 重建與交付

[文件索引](README.md) · [模型與列印清單](../output/README.md)

以下命令從 repo 根目錄執行。只使用已附的 STEP／STL 時，直接下載 [output/](../output/) 即可。

## 安裝環境

建議先建立 Python 虛擬環境，再安裝 [requirements.txt](../requirements.txt)。CAD 核心固定為 CadQuery 2.7.0；Python 版本需符合其套件支援範圍。

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell 的啟用命令為 `.venv\Scripts\Activate.ps1`。PDF 和中文檢查圖的腳本另使用 Linux 路徑 `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`，PDF 還需要同目錄的 `NotoSansCJK-Bold.ttc`；Ubuntu 可透過 `fonts-noto-cjk` 套件取得。其他系統需在對應繪圖腳本中調整字型路徑。

## 生成與檢查模型

先保留 [upstream/](../upstream/)、[reference/](../reference/)及根目錄的參數、來源清單。依序執行：

```sh
python scripts/build.py
python scripts/check_and_render.py
python scripts/check_gears.py
python scripts/validate_motion.py
python scripts/verify_delivery.py
python scripts/verify_screw_access.py
python scripts/verify_revision.py
```

`validate_motion.py` 使用 `check_gears.py` 產生的本版接觸邊界資料，因此兩者順序不可交換。檢查結果存放在 `output/validation/`，各報告用途見[驗證索引](validation.md)。這些是 CAD 檢查，實物試印流程見[裝配說明](assembly.md)。

## 更新預覽與 PDF

上述檢查通過後執行：

```sh
python scripts/plot_gear_review.py
python scripts/make_guide.py
```

產物包括 `output/preview/` 的裝配圖、齒輪對比圖、試裝板圖和 `output/裝配與試印指南.pdf`。

## 打包目前交付檔

已附的 R2 模型與驗證報告可以直接打包；修改模型後，先完成前述重建及檢查。

```sh
python scripts/package_delivery.py
```

產物集中到忽略提交的 `dist/`：

| 檔案 | 內容 |
|---|---|
| `IPX896HV_2DOF_R2.zip` | 模型、試片、文件、程式、來源及比對基準 |
| `IPX896HV_2DOF_R2.step` | 整機裝配 |
| `IPX896HV_R2_裝配與試印指南.pdf` | 中文指南 |
| `IPX896HV_2DOF_R2_preview.png` | 整機預覽 |
| `IPX896HV_R2_gear_review.png` / `.pdf` | 齒輪對比圖 |

也可指定交付目錄：

```sh
python scripts/package_delivery.py --output-dir /tmp/gripper-delivery
```

打包程式會更新根目錄的 `DELIVERY_SHA256SUMS.txt`，將它一併放入 ZIP，並檢查 ZIP 的 CRC 和各檔案 SHA-256。Git 中的交付清單應與同次提交的檔案同步更新。工作檔、快取及 `dist/` 不會進入交付包。

在 repo 根目錄或解壓後的 `IPX896HV_2DOF_R2/` 目錄，可用支援的系統工具檢查：

```sh
sha256sum -c DELIVERY_SHA256SUMS.txt
```

## 腳本索引

| 腳本 | 職責 |
|---|---|
| [build.py](../scripts/build.py) | 由來源 CAD 與參數生成主要零件、試片及完整裝配 |
| [gears.py](../scripts/gears.py) | 匹配漸開線齒圈和軸心配置的共用幾何函式 |
| [motion.py](../scripts/motion.py) | 連桿閉合與裝配姿態的共用函式 |
| [check_and_render.py](../scripts/check_and_render.py) | 靜態干涉、網格檢查及裝配渲染 |
| [check_gears.py](../scripts/check_gears.py) | 匯出齒面、齒寬重疊與剛體回程估算 |
| [validate_motion.py](../scripts/validate_motion.py) | 抽樣開合、接觸邊界及轉向干涉 |
| [verify_delivery.py](../scripts/verify_delivery.py) | 來源雜湊、STEP 重新匯入及 STL 幾何 |
| [verify_screw_access.py](../scripts/verify_screw_access.py) | 舵盤螺絲裝入路徑 |
| [verify_revision.py](../scripts/verify_revision.py) | 相對 R1 的幾何保留範圍 |
| [plot_gear_review.py](../scripts/plot_gear_review.py) | R1／R2 齒輪檢查圖 |
| [make_guide.py](../scripts/make_guide.py) | 裝配預覽及六頁中文 PDF |
| [package_delivery.py](../scripts/package_delivery.py) | 交付 ZIP、單獨預覽檔及 SHA-256 清單 |
