# 驗證報告索引

[文件索引](README.md) · [重建步驟](build.md) · [齒輪檢查圖](../output/preview/gear_review_R2.pdf)

以下為目前已提交的 R2 CAD 結果。修改參數或模型後，需重新執行對應腳本更新報告。

| 報告 | 內容 |
|---|---|
| [build_inventory.json](../output/validation/build_inventory.json) | 12 種主要零件、14 件數量，修改件實體與來源 STL 的對應 |
| [static_and_mesh.json](../output/validation/static_and_mesh.json) | 名義裝配的實體干涉、23 個 STL 的封閉性與正體積 |
| [gear_engagement.json](../output/validation/gear_engagement.json) | 145 個名義齒面位置、73 個輸入角度的雙向接觸邊界及回程估算 |
| [motion.json](../output/validation/motion.json) | 13 個名義開合姿態、20 個開合機構接觸邊界姿態、3 個轉向姿態 |
| [delivery.json](../output/validation/delivery.json) | 20 個來源檔案雜湊、20 個 STEP 匯入、23 個 STL 方向及 4 種沿用網格 |
| [screw_access.json](../output/validation/screw_access.json) | 4 個 M3 舵盤螺絲頭裝入路徑 |
| [revision_scope.json](../output/validation/revision_scope.json) | R1 保留件與原齒輪接口的幾何差異 |
| [datums.json](../output/validation/datums.json) | 舵機、傳動軸及裝配基準位置 |
| [tooth_profiles.json](../output/validation/tooth_profiles.json) | 從匯出 BRep 擷取的齒面截面，供檢查與繪圖使用 |

## 已檢查的範圍

- 相對開合行程為 0–36°。齒面截面每 0.25° 抽樣，齒輪鏈接觸邊界每 0.5° 抽樣；整體開合機構另檢查 13 個名義位置及 20 個正反向接觸邊界姿態。
- 轉向抽樣為 −45°、0°、+45°。
- 名義裝配實體穿透報告門檻為 0.01 mm³，運動干涉報告門檻為 0.02 mm³。
- R2 齒輪鏈輸出端幾何回程約 2.75°，符合暫定 ≤3° 的 CAD 目標。大齒輪與小齒輪工作齒寬重疊 2 mm，小齒輪之間為 3 mm。
- 相對 R1 更換 M01、M02、M05、M06 ×2。保留件與輪轂、中心接口、連桿的幾何比對見 `revision_scope.json`。

## 仍需實物確認

CAD 抽樣檢查尚未驗證舵機和舵盤實際尺寸、打印公差、摩擦、軸孔晃動、線材掃掠、彈性變形及負載性能，也不保證完整連續行程。未給出已驗證的載重額定值。

先按[試印及裝配步驟](assembly.md)核對接口，再進行空載測試與端點校準。原始 R1 比較資料保留於 [reference/](../reference/README.md)。
