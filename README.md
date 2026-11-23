# LAND CEX Parsing Skill

通过 Python 调用 LANDCex DLL 获取电池测试数据。技能包含 x86/x64 DLL、LANHE.sys、离线 comtypes 依赖、DLL 绑定脚本和字段说明。数据如何统计、导出成什么文件、采用什么表格样式，由 Agent 按客户要求编写任务代码。

从 [GitHub 仓库](https://github.com/who-meng/land-cex-parsing-skill) 安装，或[下载完整 ZIP](https://github.com/who-meng/land-cex-parsing-skill/archive/refs/heads/main.zip)，解压后将目录改名为 `land-cex` 并导入 Agent 客户端。更新时替换完整包。

## 首次使用

预先安装 Windows Python 3.12，在技能目录运行：

```powershell
py -3.12 -m pip --isolated install --no-index --no-deps --no-compile --target ./deps/1 ./wheels/comtypes-1.4.15-py3-none-any.whl
```

使用 32 位 Python 时改为 `py -3.12-32`。此命令仅从包内 wheel 安装 comtypes 到 `deps/1`，不访问 PyPI。首次配置执行一次，正常解析无需重复安装。DLL 位数随 Python 进程位数选择；Linux 使用 Wine 内的 Windows Python，详见[环境说明](references/platform.md)。

## 读取示例

Agent 将 `scripts` 加入 Python 模块搜索路径后，直接使用 DLL 方法：

```python
from native_cex import native_runtime

with native_runtime() as sdk:
    with sdk.open(r"D:\data\test.cex") as handle:
        sdk.check_column(handle, 16392)
        if sdk.GetRows(handle, 16392) > 0:
            voltage = sdk.value(sdk.GetDataEx, handle, 16392, 0)
            unit = sdk.value(sdk.GetUnitNameOfColumn, handle, 16392)
            print(voltage, unit)
```

脚本处理 DLL 加载、原生类型和句柄释放。时间及工步模式的展示转换使用 `sdk.display_value`，保留原始值供计算。

[技能使用规则](SKILL.md) · [DLL 调用示例](references/python-api.md) · [字段目录](references/fields.md)
