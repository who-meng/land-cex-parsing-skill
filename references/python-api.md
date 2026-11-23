# Python 调用 DLL

`native_cex.py` 绑定包内 DLL 的函数签名。调用时使用 SDK 的方法名和参数，不经过请求协议或表格组装层。

## 加载和释放

先在技能根目录执行下例初始化。后续代码块沿用这里的导入和 `source`，每个代码块自己打开并释放句柄。若从其他目录启动，将 `skill` 改为实际技能根目录的绝对路径。示例 CEX 仅供本机验证，不随包分发。

```python
import ctypes
import json
import sys
from pathlib import Path

skill = Path.cwd().resolve()
sys.path.insert(0, str(skill / "scripts"))
from native_cex import native_runtime, CexError

source = Path(r"D:\LAND\ReadCexTest\_001_1.cex")
with native_runtime() as sdk:
    with sdk.open(source, unit_scheme=-1) as handle:
        count = sdk.GetRows(handle, 16392)
```

`native_runtime` 加载 DLL 并隔离配置。`sdk.open` 将源文件复制到任务临时目录，调用 `LoadData`，退出时 `FreeData`；原文件不承担 SDK 索引写入。`brief=True` 优先使用 `LoadBriefInfo/FreeBriefInfo`，概要加载失败时通过完整加载取得诊断。多个文件可在一个运行时内依次 `sdk.open`，各自保留一个数据句柄。

单位方案沿用 SDK：`-1` 为 Auto（默认），`0` 为 mA，`1` 为 A，`2` 为 uA。输入使用绝对 `.cex` 或 `.icex` 路径；索引文件不一定能独立读取。提前确定输入和输出绝对路径，避免 SDK 临时工作目录影响路径解析。运行时和句柄不能并发或跨线程使用，也不能在退出 `with` 后使用。

## 读取字段和单个值

```python
with native_runtime() as sdk:
    with sdk.open(source) as handle:
        column_id = 8195
        sdk.check_column(handle, column_id)
        rows = sdk.GetRows(handle, column_id)
        description = sdk.value(sdk.GetDescriptionOfColumn, column_id)
        unit = sdk.value(sdk.GetUnitNameOfColumn, handle, column_id)
        if rows > 0:
            raw = sdk.value(sdk.GetDataEx, handle, column_id, 0)
            shown = sdk.display_value(handle, column_id, raw)
```

- `check_column` 校验当前字段目录与实际辅助通道绑定数；每列在读取前调用一次即可。未知 ID 抛 `E_UNKNOWN_COLUMN`，未绑定通道抛 `E_CHANNEL_UNBOUND`。
- `GetRows` 返回字段所属子表的行数，不能据此判断未知字段是否存在。循环、工步、记录行索引各自从 0 开始，读取前确保 `0 <= row_index < rows`。
- `value(fn, *args)` 为带 VARIANT 输出参数的函数分配和转换结果。原生返回失败、空值或非有限数值时返回 `None`，正常零值保留为 0。
- 需要原始返回状态和 VARIANT 类型时，直接调用绑定函数，不经过 `value`：

```python
with native_runtime() as sdk:
    with sdk.open(source) as handle:
        column_id, row_index = 16392, 0
        sdk.check_column(handle, column_id)
        if not 0 <= row_index < sdk.GetRows(handle, column_id):
            raise IndexError("Record index is outside the valid range.")
        variant = sdk.variant()
        success = sdk.GetDataEx(handle, column_id, row_index, ctypes.byref(variant))
        variant_type = variant.vt
```

`VARIANT` 的值须在活动句柄内部取得并转换为普通 Python 值后再保存。对记录逐行循环时，可由任务代码自行写 CSV、Excel 或其他目标；本技能不提供固定导出方法、输出列或表格格式。

## 展示规则

`display_value(handle, column_id, value)` 只转换一个值，不增加字段或组装行。工步模式 `8194` 通过 `GetDescriptionOfMode` 转为名称；工步时间 `8195`、测试时间 `16386`、步骤时间 `16387` 等时长按 `IsTimeHighResolution` 的文件精度显示秒或毫秒。测试时间跨天显示如 `1-01:00:00.000`，工步及步骤时间使用累计小时如 `25:00:00.000`。

计算用原始值，交给用户时默认用展示值。以下三个字段是同一记录的系统日期时间，不是时长，`display_value` 保持它们的 SDK 原值：

| 字段 ID / 名称 | SDK 类型 / Python 类型 | 处理方式 |
|---|---|---|
| `16395` / `Rec.SysTime` | `VT_BSTR (8)` / `str` | 已格式化日期字符串，例如 `2026/10/19 14:06:45`，不可再次作为秒数换算 |
| `16399` / `Rec.SysTimeAsLong` | `VT_I4 (3)` / `int` | epoch 秒，按明确的目标时区转为日期时间 |
| `16402` / `Rec.SysTimeAsDouble` | `VT_R8 (5)` / `float` | epoch 秒，保留浮点精度，按明确的目标时区转为日期时间 |

`GetStartTime/GetEndTime` 同样返回 epoch 秒，`-1` 表示未取得。日期字符串的显示受 SDK/运行环境影响，不能自行认定它是 UTC；需要统一时区时使用数值字段，并明确目标时区。日期排布和格式由用户需求决定；缺值 `None` 不进行日期转换。

## 无字段 ID 的接口

| 需求 | DLL 方法和调用方式 |
|---|---|
| 电池条码、批号 | `sdk.value(sdk.GetBattNo, handle)`、`sdk.value(sdk.GetBattBatchNo, handle)` |
| 起止时间 | `sdk.GetStartTime(handle)`、`sdk.GetEndTime(handle)`；原始 epoch 秒，`-1` 表示未取得；结束时间为估计值 |
| 备注、量程描述 | `sdk.value(sdk.GetChlNote, handle)`、`sdk.value(sdk.GetDescriptionOfVIRange, handle)` |
| 工步模式说明 | `sdk.value(sdk.GetDescriptionOfMode, mode)` |
| 活性物质 | `GetActMaterialMass` 返回质量 g，输出指针返回标称比容量 mAh/g，示例见下 |
| 通道 | `GetChannelEx` 使用箱号、通道号和其他原生输出指针；成功后箱号、通道号分别加 1，作为面向用户的编号 |
| 辅助通道数与值 | `GetDataOfAuxChls`、`GetDataOfExAuxChls`，详见[动态通道](fields.md#动态通道) |

```python
import ctypes

with native_runtime() as sdk:
    with sdk.open(source, brief=True) as handle:
        barcode = sdk.value(sdk.GetBattNo, handle)
        batch = sdk.value(sdk.GetBattBatchNo, handle)
        nominal_capacity = ctypes.c_float()
        mass_g = sdk.GetActMaterialMass(handle, ctypes.byref(nominal_capacity))
        specific_capacity = nominal_capacity.value
```

使用多个输出指针时需要显式分配 ctypes 对象，例如：

```python
with native_runtime() as sdk:
    with sdk.open(source, brief=True) as handle:
        box = ctypes.c_uint8()
        channel = ctypes.c_uint8()
        ok = sdk.GetChannelEx(handle, ctypes.byref(box), ctypes.byref(channel), None, None)
        box_number = int(box.value) + 1 if ok else None
        channel_number = int(channel.value) + 1 if ok else None
```

箱号和通道号原值从 0 开始，面向用户统一显示上述从 1 开始的 `box_number` 和 `channel_number`。例如原值 `0 / 0` 显示为 `1 / 1`，原值 `40 / 0` 显示为 `41 / 1`。转换只执行一次；读取失败时两者为 `None`。使用 Python 整数做加法，不将展示编号写回 uint8 指针，避免 255 加 1 后溢出。

## 辅助通道缓冲区

以下两段读取第 0 条记录的辅温（`kind=2`）。其他类型见[动态通道](fields.md#动态通道)。必须使用同一个活动详细句柄先查询数量，再分配 `ctypes.c_float * count` 数组。DLL 没有缓冲区长度参数，不能传入单个 `c_float` 冒充数组；数量为 0 时跳过读取。读取前检查记录行索引，读后检查返回数量。

内部辅助通道；这里不需要通道标识，因此两个可选的 `short*` 输出传 `None`：

```python
with native_runtime() as sdk:
    with sdk.open(source) as handle:
        row_index, kind = 0, 2
        count = sdk.GetDataOfAuxChls(handle, 0, kind, None, None, None)
        if count < 0:
            raise RuntimeError("Could not query internal auxiliary channels.")
        aux_values = []
        if count > 0:
            if not 0 <= row_index < sdk.GetRows(handle, 16385):
                raise IndexError("Record index is outside the valid range.")
            values = (ctypes.c_float * count)()
            returned = sdk.GetDataOfAuxChls(handle, row_index, kind, values, None, None)
            if returned != count:
                raise RuntimeError("Unexpected internal auxiliary channel count.")
            aux_values = list(values)
        print("internal temperatures:", aux_values)
```

外部辅助通道采用相同分配方式：

```python
with native_runtime() as sdk:
    with sdk.open(source) as handle:
        row_index, kind = 0, 2
        count = sdk.GetDataOfExAuxChls(handle, 0, kind, None)
        if count < 0:
            raise RuntimeError("Could not query external auxiliary channels.")
        ex_aux_values = []
        if count > 0:
            if not 0 <= row_index < sdk.GetRows(handle, 16385):
                raise IndexError("Record index is outside the valid range.")
            values = (ctypes.c_float * count)()
            returned = sdk.GetDataOfExAuxChls(handle, row_index, kind, values)
            if returned != count:
                raise RuntimeError("Unexpected external auxiliary channel count.")
            ex_aux_values = list(values)
        print("external temperatures:", ex_aux_values)
```

数组顺序为该类型内的通道顺序，内部与外部数量分别查询。以上读取保留 DLL 数值，不自行判定零值无效。多行读取可在同一个句柄内复用对应数组，每次处理本行后再读取下一行；不要将数组长度套用到另一文件。需要内部通道标识时，另外分配两个等长的 `ctypes.c_int16 * count` 数组作为箱号、通道号输出。

## 关联定位

以下方法使用原生 0 起点索引。调用前检查入口索引边界，返回负数表示没有对应关联。

- `GetCycleFromStep(handle, step_index)` 返回循环索引。
- `GetCycleFromRec(handle, record_index, step_pointer)` 返回循环索引，并填充工步索引。
- `GetFirstRecOfCycle` / `GetLastRecOfCycle`、`GetFirstRecOfStep` / `GetLastRecOfStep` 返回对应记录边界。
- `GetFirstChargeStepOfCycle` / `GetLastChargeStepOfCycle` 返回充电工步边界，不据此断言中间所有工步的模式。

```python
with native_runtime() as sdk:
    with sdk.open(source) as handle:
        if sdk.GetRows(handle, 16385) > 0:
            step = ctypes.c_int32(-1)
            cycle = sdk.GetCycleFromRec(handle, 0, ctypes.byref(step))
```

## 错误

完成上方初始化后，可用以下方式捕获读取失败。短提示面向用户，完整诊断供 Agent 排查；输出方式可按客户任务调整，不是新增交互协议。示例失败时退出码为 1，成功时为 0。

```python
try:
    with native_runtime() as sdk:
        with sdk.open(source) as handle:
            sdk.check_column(handle, 16392)
            print("rows:", sdk.GetRows(handle, 16392))
            if sdk.warning is not None:
                print(json.dumps(sdk.warning, ensure_ascii=False), file=sys.stderr)
except CexError as error:
    print(f"{source.name}: {error.payload['message']}", file=sys.stderr)
    print(json.dumps(error.payload, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(1)
```

`CexError.payload` 包含 `code/message`。加载空句柄时 `code=E_LOAD_FAILED`、`message=加载失败`，保留立即取得的 `native_code/native_message`。成功加载的告警在 `sdk.warning`。其他操作不借用 `GetLastLoadError` 解释错误。批量文件的继续、停止和结果组织由任务代码决定。

[原生错误码](load-errors.md) · [字段目录](fields.md) · [运行环境](platform.md)
