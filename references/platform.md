# Linux / Wine 与 x86、x64 调用

## Windows

按 **Python 进程位数** 选择 DLL。`py -3.12-64` 使用 `windows-x64/LANDCex_x64.dll`，`py -3.12-32` 使用 `windows-x86/LANDCex_32.dll`。`native_runtime` 自动选择并加载同目录的 `LANHE.sys`。首次使用按 [README](../README.md) 的 pip 命令安装包内依赖。`comtypes` 提供 DLL 接口使用的 COM 数据类型。

## Linux（x86-64 主机）

Linux 端使用 Wine 运行 **Windows 版 CPython 3.12**。以下以 Ubuntu/Debian 为例。x64 路线使用系统的 `wine`、`wine64` 包。x86 路线还需要宿主发行版的 32 位 Wine 支持。传统 multilib 安装方式如下，按所需位数执行。

```bash
# x64
sudo apt-get update && sudo apt-get install wine wine64
# Additional packages for x86 on Debian/Ubuntu multilib
sudo dpkg --add-architecture i386
sudo apt-get update && sudo apt-get install wine32:i386
```

为所选架构建立独立的新前缀。前缀、Python 和 DLL 的组合在同一任务中保持一致。示例使用用户通过 python.org 下载并核对的 Windows 安装程序，`INSTALLER` 指向它的 Linux 绝对路径。无桌面的服务端如需虚拟显示，可用 `xvfb-run -a` 运行初始化和安装命令。

```bash
export WINEARCH=win64 WINEPREFIX="$HOME/.wine-land-cex64"
INSTALLER="$HOME/Downloads/python-3.12.10-amd64.exe"
# For x86 instead use WINEARCH=win32, a fresh .wine-land-cex32 prefix,
# and the python-3.12.10.exe (x86) installer.
wineboot -u
wine "$INSTALLER" /quiet InstallAllUsers=0 'TargetDir=C:\Python312' Include_launcher=0 Include_pip=1 Include_test=0
PYWIN='C:\Python312\python.exe'
wine "$PYWIN" -c 'import sys,struct; print(sys.platform,struct.calcsize("P")*8)'
```

`win32 64` 表示 Windows x64 Python，`win32 32` 表示 Windows x86 Python。下面从解压后的技能根目录执行。`winepath -w` 使用同一个 `WINEPREFIX`，把 Linux 端的脚本和源文件路径转成 Windows Python 可见的绝对路径。

```bash
SKILL="$(pwd)"
WHEEL="$(winepath -w "$SKILL/wheels/comtypes-1.4.15-py3-none-any.whl")"
DEPS="$(winepath -w "$SKILL/deps/1")"
wine "$PYWIN" -m pip --isolated install --no-index --no-deps --no-compile --target "$DEPS" "$WHEEL"
SCRIPTS="$(winepath -w "$SKILL/scripts")"
INPUT="$(winepath -w "$SKILL/examples/_001_1.cex")"
wine "$PYWIN" -X utf8 -B - "$SCRIPTS" "$INPUT" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
from native_cex import native_runtime
with native_runtime() as sdk:
    with sdk.open(sys.argv[2]) as handle:
        sdk.check_column(handle, 16392)
        print(sdk.GetRows(handle, 16392))
PY
```

`wine32 is missing` 表示当前 Wine 安装缺少传统 x86 支持。`Bad EXE format` 或 Windows 错误 193 时，先检查正在运行的 Python 位数和 DLL 架构。`ModuleNotFoundError` 时用上面的离线 pip 命令为同一个解释器安装依赖。

## 更新包内 DLL

以下工作由维护者在发布前完成，客户更新时下载完整包即可。

1. 成对更新 `runtime/windows-x86/LANDCex_32.dll`、`runtime/windows-x64/LANDCex_x64.dll` 及各自目录中的 `LANHE.sys`，确认两种位数来自同一 SDK 发布。保留上一个可用包以便回退。
2. 核对 `scripts/native_cex.py` 的 `DLLS`（两个 DLL 的 SHA256）和 `SYS_HASH`。当前两个架构共用一个 SYS 哈希，因此两份 SYS 必须相同。哈希校验防止文件混装；更换文件时同步更新这些值，不要求客户手工编辑。
3. 用两个架构各自的 `GetDllVersion` 返回值核对 `SDK_VERSION`，不能拿 Windows 文件属性中的产品版本替代接口版本。逐项核对 SDK 头文件/导出定义与 `NativeCex` 中的 ctypes 函数签名，包括调用约定、参数、返回值和输出指针；当前绑定的方法必须全部存在。只有二进制内容变化、接口未变时，无需凭空修改版本或签名。
4. 字段新增或定义变更时，同步 `scripts/fields.json`、`references/fields-cycle.md`、`fields-step.md`、`fields-rec.md` 和 `fields.md` 的目录数量、说明。错误码变化时同步 `references/load-errors.md`；展示语义变化时同时核对 `display_value` 和调用说明。
5. 用 32/64 位 Windows Python 分别验证完整包：安装依赖、加载样本、读取数值/单位/中文、时间和工步名称、辅助通道、加载失败诊断及原文件哈希不变。Linux/Wine 兼容性需在对应环境实测；没有真实样本覆盖的功能如实记录。安装目录命名为 `land-cex`，用开发环境的 `skills-ref validate <技能目录>` 验证 Skill 格式；Windows PowerShell 先设置 `$env:PYTHONUTF8='1'`，确保校验器按 UTF-8 读取中文文档。
6. 将验证后的完整文件作为一次 Git 提交推送到本仓库，客户从同一入口更新完整包。不要只替换 DLL 而留下旧哈希、旧绑定或旧字段目录。Skill 无独立版本号，Git 提交记录用于追踪哪组文件一起发布。

可以用 PowerShell `Get-FileHash -Algorithm SHA256 <文件路径>` 取得二进制哈希。这里只维护当前完整包，不要求客户配置下载服务器或手工拼装依赖。
