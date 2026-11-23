# LAND CEX Parsing Skill

此包包含 Skill 文档、Python 解析脚本、Windows x86/x64 LANDCex DLL、LANHE.sys，以及 comtypes 的离线安装包。Python 解释器需预先安装，推荐 Windows Python 3.12。

读取和导出时自动处理显示格式：工步时间、测试时间和步骤时间显示为时分秒，按文件精度保留毫秒；工步模式在原列中显示工步名称。

Skill 及配套依赖统一从 [who-meng/land-cex-parsing-skill](https://github.com/who-meng/land-cex-parsing-skill) 下载，解析时使用本地 DLL。

支持 GitHub 技能安装的 Agent 客户端可填写仓库地址 `https://github.com/who-meng/land-cex-parsing-skill`。也可[下载完整 ZIP](https://github.com/who-meng/land-cex-parsing-skill/archive/refs/heads/main.zip)，解压后将 `land-cex-parsing-skill-main` 文件夹改名为 `land-cex`，再导入客户端。更新时重新下载完整包。

## 首次使用

在解压得到的 land-cex 目录中执行：

```powershell
py -3.12 -B scripts/install-deps.py
```

此命令只从包内 wheels 安装依赖到本包 deps/1，不访问 PyPI。随后将 land-cex 导入 Agent 客户端。若使用 32 位 Python，改用 `py -3.12-32` 执行同一命令。

Agent 将 scripts 加入 Python 模块搜索路径，通过 `from land_cex import open_cex` 使用解析接口。DLL 位数由运行 Python 的位数决定。Linux 仍需 Wine 内的 Windows Python，本包不提供 Linux 原生解析器。

## 读取数据

Agent 直接运行 Python，读取结果是 Python 对象。例如读取工步模式和工步时间：

```python
from land_cex import open_cex

with open_cex(r"D:\data\test.cex") as f:
    for mode, duration in f.iter_export_rows("step", [8194, 8195]):
        print(mode, duration)
```

文件加载、句柄释放、模式名称及时间格式均由脚本处理。需要其他 DLL 功能时，可在同一会话内通过 `sdk, handle = f.native` 调用。

[使用规则](SKILL.md) · [Python 接口](references/python-api.md) · [字段目录](references/fields.md)
