---
name: land-cex
description: 通过 LANDCex DLL 读取 LAND 电池测试文件（.cex）的循环、工步、记录、单位、条码、批号和活性物质数据，供 Agent 按用户要求处理。
compatibility: 需要 Windows Python 3.12 和 comtypes；支持 x86/x64。Linux 使用 Wine 运行 Windows Python。
---

# LAND CEX 数据访问

将本技能的 `scripts` 加入 Python 搜索路径，从 `native_cex` 导入 `native_runtime`。首次配置见 [README](README.md)。技能负责调用 DLL 获取数据，字段选择、统计、文件格式、表头和排布由 Agent 按用户需求决定。

```python
from native_cex import native_runtime

with native_runtime() as sdk:
    with sdk.open(source) as handle:
        column_id = 16392
        sdk.check_column(handle, column_id)
        count = sdk.GetRows(handle, column_id)
        unit = sdk.value(sdk.GetUnitNameOfColumn, handle, column_id)
        if count > 0:
            value = sdk.value(sdk.GetDataEx, handle, column_id, 0)
```

- 输入文件使用绝对路径；在进入 `native_runtime()` 前确定所有输入、输出路径。SDK 工作期间会临时改变工作目录。同一进程一次使用一个运行时，句柄仅在所属 `with` 中、当前线程使用。
- `sdk.open(source)` 默认单位方案为 Auto；可传 `unit_scheme=0/1/2` 分别选择 mA/A/uA。概要查询用 `brief=True`。数据对象自动释放，多文件可在同一个运行时内依次打开。
- 从[字段目录](references/fields.md)匹配用户需求。字段含义、层级、通道或单位有歧义时先向用户确认，不猜 ID。每个字段在读取前调用一次 `check_column`，检查未知 ID 和未绑定辅助通道。
- 循环、工步、记录的原生行索引各自从 **0** 开始。用 `GetRows` 确定边界，不按相同行号拼接不同层级；需要关联时调用 DLL 的定位接口。
- 计算使用 `sdk.value(...)` 的原始值；面向用户展示时使用 `sdk.display_value(handle, column_id, value)`。工步模式 `8194` 转为名称，时间字段按文件精度转为时分秒；不额外添加名称列。用户明确要求原始码或秒数时保留原值。
- 查询实际单位后再解释或合并数据。SDK 返回零就保留零，不自行断言零表示无效；缺值 `None` 与零分开处理。
- 大量数据逐条读取并由任务代码写入用户指定的文件，不把全部明细打印到 Agent 上下文。逐条读取不会消除 DLL 的 `LoadData` 全量加载内存占用。
- 加载失败时提示“文件名：加载失败”。客户询问原因时依据异常的 `native_code`、`native_message` 和[错误说明](references/load-errors.md)解释，未知原因不猜测。

[DLL 调用示例](references/python-api.md) · [字段目录](references/fields.md) · [Windows / Wine 环境](references/platform.md)
