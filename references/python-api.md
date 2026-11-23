# Python 文件会话

## 默认展示规则

向用户展示、导出或自行组装表格时，使用 `iter_export_rows` 的展示值。工步模式 `8194` 在原列中显示 DLL 返回的工步名称，不增加名称列。工步时间 `8195`、测试时间 `16386`、步骤时间 `16387` 默认采用 `Auto(h:m:s)`；内部计算才用 `iter_rows` 的模式码和数值秒。不要将 `display_times=False` 的结果直接作为默认用户输出。

```python
with open_cex(source) as f:
    for mode, duration in f.iter_export_rows("step", [8194, 8195]):
        print(mode, duration)
    for test_time, step_time in f.iter_export_rows("rec", [16386, 16387]):
        print(test_time, step_time)
```

Excel 时长需要数值与格式配套，请使用 `export_xlsx`。自定义 Excel 若直接写入原始秒数，Excel 不会自动将其转换为 时分秒格式。

将本技能的 `scripts` 加入 `sys.path` 或 `PYTHONPATH` 后，可在 Windows 的 Python 3.12 中 `from land_cex import open_cex, process_files, CexError`。DLL 会临时调整进程工作目录和注册表映射，同一进程一次支持一个活动会话。封装的输入和 CSV 输出使用绝对路径。输入后缀可用 `.cex` 或 `.icex`，随 CEX 生成的索引文件可能无法独立读取。

| Python 用法 | 参数、返回值及 DLL 对应 |
|---|---|
| `with open_cex(path, *, unit_scheme="Auto", metadata_only=False) as f` | `path` 接受绝对路径字符串或 `Path`。完整读取使用一次 `LoadData`，退出自动 `FreeData`。单位方案可用 `Auto`、`mA`、`A`、`uA`。 |
| `open_cex(path, metadata_only=True)` | 面向条码、批号、起止时间、活性物质、通道、量程和备注的轻量查询。优先 `LoadBriefInfo`，SDK 无法读取文件头时沿用完整加载的诊断。 |
| `process_files(paths, process, *, unit_scheme="Auto", metadata_only=False)` | `paths` 是输入路径的可迭代对象。每个有效路径处理一次，回调 `process(source, f)` 的返回值保存在该文件结果的 `data` 中。详见下方批量示例。 |
| `f.info(*items)` | 返回字典。`start_time`、`end_time` 返回 Unix 秒，SDK 返回 -1 时为 `None`。`barcode`、`batch_no`、`channel_note`、`vi_range` 返回原文。`channel` 为箱号和通道号（如 `041_1`）。`active_material` 同时返回 `mass_g` 和 `nominal_specific_capacity_mah_g`。完整会话另支持 `aux_counts`、`exaux_counts`。 |
| `f.rows(level)` | `GetRows` 返回指定层级的整数行数。`level` 可用 `cycle`、`step`、`rec`。 |
| `f.columns(ids)` | `ids` 为非空且无重复的十进制 ID 列表或元组。按请求顺序返回 `id`、`description`、`unit`，由 SDK 提供。 |
| `f.export_columns(level, *, extra_platforms=None)` | 返回当前文件在该层可导出的列，含 `id`、`read_id`、`description`、`unit` 和面向用户的 `header`。`id` 用于 `iter_export_rows`，组合字段的 `read_id` 为 `None`。工步模式列读取 `8194` 模式码，经 `GetDescriptionOfMode` 返回名称，如 `恒流放电`。需要含参数的完整描述时，使用 `f.iter_rows([8204])`。数值主参数可按工步读 `8209`，适用的第二参数可读 `8210`。动态通道按文件绑定数筛选。 |
| `from cex_excel import export_xlsx`，`export_xlsx(f, output, *, extra_platforms=None, on_row=None, summary_ids=None)` | 写入循环、工步、记录和测试信息四张工作表。`tables` 中的 `cycle`、`step`、`rec`、`info` 各含 `rows` 和 `columns`。`output` 为新 `.xlsx` 绝对路径，记录表逐行统计见下方示例。 |
| `f.iter_export_rows(level, ids=None, *, start=1, end=None, display_times=True, extra_platforms=None, on_row=None, summary_ids=None)` | 按请求顺序返回 已格式化的展示值，支持各层导出 ID、自动时长格式和组合字段。省略 `ids` 使用该层可导出的所有列。设 `display_times=False` 可获得秒数。 |
| `f.iter_rows(ids, *, start=1, end=None)` | 在当前会话内流式读取同层字段，每行是与 `ids` 同序的 Python 列表，缺值为 `None`。默认读到该层末行。`start`、`end` 是含首尾的用户序号。内部调用 `GetDataEx`。 |
| `f.export_csv(output, ids, *, start=1, end=None, on_row=None, summary_ids=None, display_times=True)` | 支持 `f.export_columns("rec")` 返回的全部记录层 ID，包括归属、状态和充放电分项。给出父目录已存在的新 CSV 绝对路径。`display_times=False` 输出数值秒。`on_row(行号, 值元组)` 在写每行时接收 `summary_ids` 指定的记录字段，省略 `summary_ids` 时接收导出字段。返回 `output`、`rows`、`columns`。CSV 使用 UTF-8 BOM，首列记录序号从 1 开始，缺值留空。成功退出 `with` 才发布文件。 |
| `sdk, handle = f.native` | 当前架构已绑定 `ctypes` 签名的 DLL 方法及原生句柄。适用于需要直接调用的业务。资源归会话所有，仅在当前 `with`、当前线程中使用。 |
| `f.warning` | 正常加载时为 `None`。SDK 给出警告时返回 `native_api`、`native_code`、`message`。 |

例如，用户要求导出完整电压和电流并附上启动时间。使用同一文件句柄读取，等文件发布后再向用户报告。

```python
with open_cex(source) as f:
    result = f.export_csv(destination, [16392, 16388])
    result.update(f.info("start_time"))
    result["warning"] = f.warning
print(result)
```

例如，用户只要已记录的最大电压和有效记录数。下面的代码流式扫描，空值跳过，正常的零参与统计。

```python
with open_cex(source) as f:
    maximum = None
    count = 0
    for (voltage,) in f.iter_rows([16392]):
        if voltage is not None:
            count += 1
            maximum = voltage if maximum is None else max(maximum, voltage)
    unit = f.columns([16392])[0]["unit"]
    warning = f.warning
print(maximum, unit, count, warning)
```

例如，直接读取第一条记录的电流。`sdk.value` 负责申请和转换 `VARIANT`，数据缺失时返回 `None`。原生记录、工步、循环的 `Index` 字段值以及 `GetDataEx` 的行号都从 0 开始。

```python
with open_cex(source) as f:
    sdk, handle = f.native
    if sdk.GetRows(handle, 16385) > 0:
        value = sdk.value(sdk.GetDataEx, handle, 16388, 0)
        unit = sdk.value(sdk.GetUnitNameOfColumn, handle, 16388)
        print(value, unit)
```

`CexError.payload` 包含 `code`、`message`，SDK 错误可另附 `native_api`、`native_code`。`LoadData` 返回空句柄时，`message` 固定为“加载失败”，`native_code` 保留 DLL 返回的无符号 32 位整数，`native_message` 保留 DLL 说明或为 `null`。例如码 `24` 表示没有数据记录，文件头仍可用时可单独查询启动时间。见[加载错误码](load-errors.md)。Python 调用方可捕获该异常。支持的 1,985 个字段见[完整目录](fields.md)。通道绑定和数量约束见[动态通道](dynamic-fields.md)。

## 内置时间格式与组合列

时间格式由解析代码自动处理，无需调用方查询精度或拼接时间字符串。普通精度显示 `hh:mm:ss`，高精度显示 `hh:mm:ss.fff`。测试时间超过一天使用天数前缀，如 `1-01:00:00.000`；工步时间和步骤时间使用累计小时，如 `25:00:00.000`。日期时间与这些时长分别处理。

Excel 时长使用可计算的数值和对应的时间格式，超过 24 小时仍显示累计小时；负时长显示带符号的文本。缺值保持为空。

以下组合列可用 `iter_export_rows` 按 ID 选择，按请求顺序返回，不会自动增加重复的名称列：

| 层级 | ID | 含义 |
|---|---|---|
| 循环 | `0x11001` / `0x11002` | 循环开始 / 结束时间 |
| 工步 | `0x2801` | 所属循环序号 |
| 工步 | `0x2802` / `0x12001` | 工步开始 / 结束时间 |
| 记录 | `0x4802` / `0x4803` | 所属循环 / 工步序号 |
| 记录 | `0x4804` | 工步状态缩写，如 `CCC`、`CCD`、`R` |
| 记录 | `0x4805` / `0x4806` | 充电 / 放电容量 |
| 记录 | `0x4807` / `0x4808` | 充电 / 放电能量 |

序号从 1 开始。起止时间取首末已保存记录的系统时间，没有对应记录时留空。容量与能量按所属工步归入充电或放电侧，另一侧为零，单位沿用当前文件。记录主参数组合列 `0x4809` 暂不支持；需要工步参数时可使用原始读取接口查询 `8204`、`8209`、`8210`。

## 多份文件的导出和汇总

`process_files(paths, process)` 为整批加载一次 DLL，按首次出现的顺序处理去重后的绝对路径。每个文件只创建一个数据句柄，回调内完成文件头查询、导出和汇总，释放后再处理下一份文件。回调返回值可以是任意 Python 对象。文件句柄和行迭代器的有效期到回调结束。

以下回调同时导出电压、电流并求最大测试时间。`on_row(number, values)` 收到从 1 开始的原记录行号和按 `summary_ids` 顺序排列的值。SDK 每行只读取导出字段与统计字段的并集一次。省略 `summary_ids` 时，CSV 回调按调用方的 `ids` 顺序收值，Excel 回调按记录表的列顺序收值。`number` 是从 1 开始的原记录号。数值字段保留原单位和精度，时长为秒，原生 `Rec.Index` 从 0 开始，组合列的归属序号从 1 开始。若只需统计，直接迭代 `f.iter_rows(...)`。请用 `f.columns(...)` 确认实际单位后再跨文件合并数值。

```python
from land_cex import process_files

def process(source, f):
    maximum_time = None
    valid_voltages = 0

    def observe(number, values):
        nonlocal maximum_time, valid_voltages
        voltage, test_time = values
        valid_voltages += voltage is not None
        if test_time is not None:
            maximum_time = test_time if maximum_time is None else max(test_time, maximum_time)

    result = f.export_csv(outputs[source], [16392, 16388], on_row=observe, summary_ids=[16392, 16386])
    result.update(f.info("start_time"))
    result.update(max_test_time_s=maximum_time, valid_voltages=valid_voltages)
    return result

# outputs maps each resolved input Path to a distinct, absolute CSV destination.
results = process_files(outputs.keys(), process)
print(results)
```

`process_files` 返回每份文件的 `file`、`ok`、`data` 或 `error`，SDK 告警放在 `warning`。回调抛出的普通异常记入该文件的 `error` 后继续处理下一份。CSV 和 XLSX 在本文件的回调成功并关闭句柄后按请求顺序发布。回调失败时清理暂存输出。若文件发布阶段遇到重名或磁盘错误，`error.failed_output` 指出失败路径，`error.published_outputs` 列出已成功生成的路径。只需要各文件的头信息时可传 `metadata_only=True`。

CSV 首列统一为记录序号。显式选择 `16385` 时也只输出一次，区间导出保留原文件记录号。SDK 字段的表头取自 `GetDescriptionOfColumn` 和 `GetUnitNameOfColumn`，组合字段沿用 Excel 记录表的名称和单位。有单位时写作 `电压 (V)`，单位为空时仅写列名。显示名为空时取 DLL 的 `ColumnID_to_Str` 名称。首列记录序号从 1 开始，CSV 返回的 `columns` 中保留数值 ID 供程序关联。

## 四表 Excel 和逐条记录统计

```python
from cex_excel import export_xlsx
from land_cex import open_cex

with open_cex(source) as f:
    summary = {"valid_voltage": 0, "max_test_time_s": None}

    def observe(number, values):
        voltage, seconds = values
        summary["valid_voltage"] += voltage is not None
        if seconds is not None:
            previous = summary["max_test_time_s"]
            summary["max_test_time_s"] = seconds if previous is None else max(previous, seconds)

    result = export_xlsx(f, destination, on_row=observe, summary_ids=[16392, 16386])
print(result["tables"], summary)
```

Excel 在写记录表时每条记录调用一次 `observe`。统计字段既可与导出列重合，也可选同层可读的其他 SDK 字段。

默认导出充电、放电各 1、2 号平台。用户确认额外配置的方向和槽位后，例如仅追加充电 3 号和放电 4 号，调用 `export_xlsx(f, destination, extra_platforms={"charge": [3], "discharge": [4]})`。自定义导出把同一个 `extra_platforms` 传给 `export_columns` 和 `iter_export_rows`。

公开导出序号从 1 开始，三张表可按循环序号、工步序号关联。`iter_rows` 提供原始 SDK 数值，`iter_export_rows` 提供展示值。记录 CSV 的时间列采用展示格式，`on_row` 仍收到原始数值供统计。

```python
with open_cex(source) as f:
    for cycle, started, ended in f.iter_export_rows("cycle", [4096, 0x11001, 0x11002]):
        print(cycle, started, ended)
    for step, started, ended in f.iter_export_rows("step", [8193, 0x2802, 0x12001]):
        print(step, started, ended)
```

信息表按本机时区显示起止时间。“结束时间（估计）”取自 `GetEndTime`。完整加载时，SDK 根据最后一条记录的系统时间取整到秒。`GetActMaterialMass` 返回质量（g），并通过输出指针返回标称比容量（mAh/g）。信息表将质量换算成 mg，SDK 的未设置值 0 在表内留空。电池条码与电池批号按文本写入，保留前导零。

三张数据表最多各容纳 1,048,575 条数据及一行表头。[字段目录](fields.md) · [运行环境](platform.md)
