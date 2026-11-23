# LAND CEX Parsing Skill

通过 Python 调用 LANDCex DLL 获取电池测试数据。技能包含 x86/x64 DLL、LANHE.sys、离线 comtypes 依赖、DLL 绑定脚本和字段说明。数据如何统计、导出成什么文件、采用什么表格样式，由 Agent 按客户要求编写任务代码。

## 安装到 Agent 客户端

在客户端要求的技能安装位置执行：

```powershell
git clone https://github.com/who-meng/land-cex-parsing-skill.git land-cex
cd land-cex
```

也可[下载完整 ZIP](https://github.com/who-meng/land-cex-parsing-skill/archive/refs/heads/main.zip)。GitHub 解压目录通常为 `land-cex-parsing-skill-main`，请将包含 `SKILL.md` 的这一层改名为 `land-cex`，再按客户端说明放入技能目录或导入。最终结构应为 `land-cex/SKILL.md`、`land-cex/scripts/`、`land-cex/runtime/`，不要多套一层目录。

不同客户端的技能安装位置不同；支持仓库链接安装的客户端也应将技能安装名设为 `land-cex`。更新时替换完整包，保留客户自己的任务代码和数据在包外。

## 首次使用

预先安装 Windows Python 3.12，在技能目录运行：

```powershell
py -3.12 -m pip --isolated install --no-index --no-deps --no-compile --target ./deps/1 ./wheels/comtypes-1.4.15-py3-none-any.whl
```

使用 32 位 Python 时改为 `py -3.12-32`。此命令仅从包内 wheel 安装 comtypes 到 `deps/1`，不访问 PyPI。首次配置执行一次，正常解析无需重复安装。DLL 位数随 Python 进程位数选择；Linux 使用 Wine 内的 Windows Python，详见[环境说明](references/platform.md)。

## 读取示例

下面示例从包含 `SKILL.md` 的技能根目录运行，可保存为包外的 Python 脚本，用 `py -3.12 -X utf8 <脚本路径>` 执行。`Path.cwd()` 指向技能根目录；若从其他目录启动，请将 `skill` 改为实际安装的绝对路径。

包内提供[示例文件](examples/_001_1.cex)，下面的代码可直接读取。处理自己的数据时，将 `source` 改为该文件的绝对路径。

```python
import json
import sys
from pathlib import Path

skill = Path.cwd().resolve()
sys.path.insert(0, str(skill / "scripts"))
from native_cex import CexError, native_runtime

source = skill / "examples" / "_001_1.cex"
try:
    with native_runtime() as sdk:
        with sdk.open(source) as handle:
            column_id = 16392
            sdk.check_column(handle, column_id)
            count = sdk.GetRows(handle, column_id)
            print("rows:", count)
            if count > 0:
                voltage = sdk.value(sdk.GetDataEx, handle, column_id, 0)
                unit = sdk.value(sdk.GetUnitNameOfColumn, handle, column_id)
                print("voltage:", voltage, unit)
except CexError as error:
    print(f"{source.name}: {error.payload['message']}", file=sys.stderr)
    print(json.dumps(error.payload, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(1)
```

脚本处理 DLL 加载、原生类型和句柄释放。时间及工步模式的展示转换使用 `sdk.display_value`，保留原始值供计算。

[技能使用规则](SKILL.md) · [DLL 调用示例](references/python-api.md) · [字段目录](references/fields.md)

维护者更新 DLL 时，按[运行环境中的更新说明](references/platform.md#更新包内-dll)同步二进制校验、接口签名和字段目录。
