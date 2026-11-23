---
name: land-cex
description: 解析 LAND 电池测试文件（.cex）。查询启动时间、电池条码和批号，读取循环、工步及记录，批量汇总或导出电压、电流等字段到 CSV 或 Excel。
compatibility: 解析需要 Windows 版 Python 3.12 和 comtypes，导出 Excel 还需 openpyxl。Linux 使用 Wine 运行 Windows 版 Python。
---

# LAND CEX 解析

将本技能目录下的 `scripts` 加入 Python 模块搜索路径，通过 `land_cex` 直接调用 DLL。输入、输出使用绝对路径。首次配置见[安装与环境自检](README.md)。

面向用户展示和导出的数据由解析代码自动应用以下规则，无需另行格式化：

- 工步时间 `8195`、测试时间 `16386`、步骤时间 `16387` 使用 `Auto(h:m:s)`，按文件精度显示秒或毫秒。自定义表格也用 `f.iter_export_rows(...)` 取展示值，不直接输出原始秒数。
- 工步模式 `8194` 在原列中通过 `GetDescriptionOfMode` 转为工步名称，不保留数字模式码、不额外增加名称列。用户明确要求原始模式码时才取原值。
- `f.iter_rows(...)` 和 `on_row` 回调的原始数值用于计算。计算结果交给用户时，时长按时分秒显示；只有用户明确要求数值秒时才输出秒数。Excel 使用 `cex_excel.export_xlsx` 保留时长单元格格式。

| 用户需求 | Python 入口 |
|---|---|
| 只查启动时间、电池条码、电池批号或活性物质 | `with open_cex(path, metadata_only=True) as f`，用 `f.info(...)` 查文件头 |
| 展示工步名称、时长、序号或归属 | `f.iter_export_rows(level, ids)` 返回已格式化的展示值。`f.export_columns(level)` 给出可选列及表头 |
| 计算平均值、最大值或时长 | `f.iter_rows(ids)` 返回 SDK 原始值，用 `f.columns(ids)` 查本文件的单位 |
| 导出文件 | 记录明细用 `f.export_csv(output, ids)`。四表 Excel 用 `cex_excel.export_xlsx(f, output)`。两种格式都支持通过 `on_row` 和 `summary_ids` 在写记录时汇总 |

```python
from land_cex import open_cex

with open_cex(source) as f:
    ids = [c["id"] for c in f.export_columns("rec")]
    report = f.export_csv(destination, ids)
print(report["output"], report["rows"])
```

- 同一文件的读取、统计和导出共用一个会话。多文件用 `process_files(paths, process)`，每份 CEX 的回调成功结束并关闭句柄后发布文件。
- 循环平台默认导出充电、放电各 1、2 号，“导出全部”也按此处理。用户明确提到配置了更多平台时，确认方向和槽位后，用 `extra_platforms` 追加指定的 3～5 号。
- 文件加载失败时，向客户提示“文件名：加载失败”。客户询问原因时，用中文解释 `native_message`；必要时查[加载错误码](references/load-errors.md)。原生码供排查，未知原因不要猜测。批量处理时指出具体失败的文件。
- 需要底层 DLL 接口和当前句柄时使用 `sdk, handle = f.native`。

[Python 参数和批量示例](references/python-api.md) · [字段 ID 目录](references/fields.md) · [Windows / Wine 运行环境](references/platform.md)

- 从 [官方仓库](https://github.com/who-meng/land-cex-parsing-skill) 安装完整技能包，包含 x86/x64 DLL、LANHE.sys 与离线 Python 依赖。首次使用执行 `python scripts/install-deps.py`，只安装包内 wheel。解析只使用包内运行时，不发起 DLL 下载或远端更新检查。
