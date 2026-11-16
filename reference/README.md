# R1 比對基準

[專案首頁](../README.md) · [版本紀錄](../CHANGELOG.md) · [驗證報告](../docs/validation.md)

此目錄保留 R1 的比較資料，供 R2 驗證及繪圖使用。基準提交為 [`a9ed9fded2ce59b079b9b703d5fd8c7202095e94`](https://github.com/KevinQianjin/MATE-Workshop-Gripper-Design/commit/a9ed9fded2ce59b079b9b703d5fd8c7202095e94)。

| 檔案 | 用途 |
|---|---|
| [R1_parameters.json](R1_parameters.json) | R1 尺寸及齒輪裝配參數 |
| [R1_gear_engagement.json](R1_gear_engagement.json) | R1 原齒形回程估算，供 R1／R2 比較 |
| [R1_parts/](R1_parts/) | M02、M03、M04、N01、N02 的 R1 BRep 快照 |
| [R1_parts/manifest.json](R1_parts/manifest.json) | 快照來源提交與 SHA-256 |

`scripts/verify_revision.py` 先核對快照雜湊，再比較 R2 保留件與齒輪接口。修改現行設計時，應保留這些基準資料；目前可供試印的檔案位於 [output/](../output/README.md)。
