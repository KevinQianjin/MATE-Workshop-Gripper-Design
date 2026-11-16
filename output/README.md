# R2 模型與列印清單

[專案首頁](../README.md) · [裝配說明](../docs/assembly.md) · [五金 BOM](../BOM.csv)

先開[完整裝配 STEP](IPX896HV_2DOF_assembly.step)確認機構，再列印試裝件。主要列印件共 **12 種、14 件**；STEP 裝配另含 4 個 `REF_` 舵機／金屬舵盤參考包絡，這些不是列印件。

## 主要列印件

| 編號 | 零件 | 數量 | STL | 分件 STEP |
|---|---|---:|---|---|
| U01 | 左夾指 | 1 | [列印](stl/U01_left_claw.stl) | — |
| U02 | 右夾指 | 1 | [列印](stl/U02_right_claw.stl) | — |
| U03 | 被動連桿 | 2 | [列印](stl/U03_linkage_PRINT_2.stl) | — |
| U06 | 底座側壁 | 1 | [列印](stl/U06_base_wall.stl) | — |
| M01 | 掌板／舵機座 | 1 | [列印](stl/M01_palm_IPX896HV.stl) | [修改](step/M01_palm_IPX896HV.step) |
| M02 | 驅動齒輪連桿與舵盤接口 | 1 | [列印](stl/M02_drive_gear_horn_adapter.stl) | [修改](step/M02_drive_gear_horn_adapter.step) |
| M03 | 固定底座 | 1 | [列印](stl/M03_base_IPX896HV.stl) | [修改](step/M03_base_IPX896HV.step) |
| M04 | 旋轉座 | 1 | [列印](stl/M04_original_waist_horn_interface.stl) | [修改](step/M04_original_waist_horn_interface.step) |
| M05 | 右齒輪連桿 | 1 | [列印](stl/M05_right_gear_involute.stl) | [修改](step/M05_right_gear_involute.step) |
| M06 | 小齒輪 | 2 | [列印](stl/M06_small_gear_involute_PRINT_2.stl) | [修改](step/M06_small_gear_involute_PRINT_2.step) |
| N01 | 底座舵盤轉接盤 | 1 | [列印](stl/N01_yaw_horn_coupler.stl) | [修改](step/N01_yaw_horn_coupler.step) |
| N02 | 夾爪轉接支架 | 1 | [列印](stl/N02_gripper_to_waist_bridge.stl) | [修改](step/N02_gripper_to_waist_bridge.step) |

`PRINT_2` 表示同一檔案印兩件。沿用件未另匯出分件 STEP，可在完整裝配或固定的來源 STEP 中查看。R2 的 M01、M02、M05、M06 應成套使用。

## 試裝件

| 試裝檔 | 用途／數量 |
|---|---|
| [F01 舵機固定耳](fit_checks/F01_servo_ear_fit.stl) | 檢查外殼、固定耳及四孔配合，1 件 |
| [F02 舵盤與延長軸](fit_checks/F02_horn_slot_fit.stl) | 檢查金屬舵盤孔位及螺絲裝入空間，1 件 |
| [F03 軸孔環](fit_checks/F03_shaft_clearance_ring.stl)＋[F04 軸試片](fit_checks/F04_shaft_fit_pin.stl) | 檢查轉動配合，各 1 件 |
| [F05 四齒輪底板](fit_checks/F05_four_gear_trial_plate.stl) | 手動試驗齒輪配合，1 件 |
| B08：[20T](fit_checks/F_mesh_20T_B08_PRINT_2.stl)／[19T](fit_checks/F_mesh_19T_B08_PRINT_2.stl) | 每對設計切向齒隙 0.08 mm；各印 2 件 |
| **B12**：[20T](fit_checks/F_mesh_20T_B12_PRINT_2.stl)／[19T](fit_checks/F_mesh_19T_B12_PRINT_2.stl) | **本版主零件採用**，設計齒隙 0.12 mm；各印 2 件 |
| B16：[20T](fit_checks/F_mesh_20T_B16_PRINT_2.stl)／[19T](fit_checks/F_mesh_19T_B16_PRINT_2.stl) | 設計齒隙 0.16 mm；各印 2 件 |

先試 B12，同一組四個齒輪使用相同代號。這些數字是 CAD 設計值；選用其他齒隙需要重建並驗證主齒輪。步驟見[齒輪試裝與選配](../docs/assembly.md#齒輪試裝與選配)。各試裝件的 STEP 也放在 [fit_checks/](fit_checks/)。

## 其他檔案

| 路徑 | 內容 |
|---|---|
| [裝配與試印指南.pdf](裝配與試印指南.pdf) | 六頁中文圖文指南 |
| [preview/](preview/) | 裝配預覽、三視圖、齒輪檢查圖及試裝板示意 |
| [validation/](validation/) | CAD 與交付檢查 JSON；見[報告索引](../docs/validation.md) |
| [brep/](brep/) | 腳本生成的精確幾何快照，用於檢查與渲染 |

檔名前綴：`U` 為保留原幾何、`M` 為局部修改、`N` 為新增轉接件、`F` 為試裝件。STL 已安排初始列印方向；切片設定與支撐仍需按[列印建議](../docs/assembly.md#列印建議)確認。
