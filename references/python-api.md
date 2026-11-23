# Python 调用 DLL

`native_cex.py` 绑定包内 DLL 的函数签名。调用时使用 SDK 的方法名和参数，不经过请求协议或表格组装层。

## 加载和释放

```python
from pathlib import Path
from native_cex import native_runtime, CexError

source = Path(r"D:\data\test.cex")
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
import ctypes

variant = sdk.variant()
success = sdk.GetDataEx(handle, column_id, row_index, ctypes.byref(variant))
variant_type = variant.vt
```

上述代码在活动句柄内部运行，`row_index` 必须先检查边界。对记录逐行循环时，可由任务代码自行写 CSV、Excel 或其他目标；本技能不提供固定导出方法、输出列或表格格式。

## 展示规则

`display_value(handle, column_id, value)` 只转换一个值，不增加字段或组装行。工步模式 `8194` 通过 `GetDescriptionOfMode` 转为名称；工步时间 `8195`、测试时间 `16386`、步骤时间 `16387` 等时长按 `IsTimeHighResolution` 的文件精度显示秒或毫秒。测试时间跨天显示如 `1-01:00:00.000`，工步及步骤时间使用累计小时如 `25:00:00.000`。

计算用原始值，交给用户时默认用展示值。系统时间、开始时间、结束时间按各自 SDK 类型解释，与时长分开处理；日期格式由任务决定。

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

使用多个输出指针时需要显式分配 ctypes 对象，例如在活动句柄内：

```python
box = ctypes.c_uint8()
channel = ctypes.c_uint8()
ok = sdk.GetChannelEx(handle, ctypes.byref(box), ctypes.byref(channel), None, None)
box_number = int(box.value) + 1 if ok else None
channel_number = int(channel.value) + 1 if ok else None
```

箱号和通道号原值从 0 开始，面向用户统一显示上述从 1 开始的 `box_number` 和 `channel_number`。例如原值 `0 / 0` 显示为 `1 / 1`，原值 `40 / 0` 显示为 `41 / 1`。转换只执行一次；读取失败时两者为 `None`。使用 Python 整数做加法，不将展示编号写回 uint8 指针，避免 255 加 1 后溢出。

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

`CexError.payload` 包含 `code/message`。加载空句柄时 `code=E_LOAD_FAILED`、`message=加载失败`，保留立即取得的 `native_code/native_message`。成功加载的告警在 `sdk.warning`。其他操作不借用 `GetLastLoadError` 解释错误。批量文件的继续、停止和结果组织由任务代码决定。

[原生错误码](load-errors.md) · [字段目录](fields.md) · [运行环境](platform.md)
