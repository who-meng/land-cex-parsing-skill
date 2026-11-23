# Linux / Wine 与 x86、x64 调用

## Windows

按 **Python 进程位数** 选择 DLL。`py -3.12-64` 使用 `windows-x64/LANDCex_x64.dll`，`py -3.12-32` 使用 `windows-x86/LANDCex_32.dll`。`land_cex` 自动选择并加载同目录的 `LANHE.sys`。用所选解释器运行 `-B scripts/install-deps.py`。`comtypes` 提供 DLL 接口使用的 COM 数据类型。

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

`win32 64` 表示 Windows x64 Python，`win32 32` 表示 Windows x86 Python。下面从解压后的技能根目录执行。`winepath -w` 使用同一个 `WINEPREFIX`，把 Linux 端的脚本、源文件和输出路径转成 Windows Python 可见的绝对路径。输出目录需已存在。

```bash
SKILL="$(pwd)"
INSTALL_DEPS="$(winepath -w "$SKILL/scripts/install-deps.py")"
wine "$PYWIN" -B "$INSTALL_DEPS"
SCRIPTS="$(winepath -w "$SKILL/scripts")"
INPUT="$(winepath -w '/data/_041_1.cex')"
OUTPUT="$(winepath -w '/data/output/_041_1.csv')"
wine "$PYWIN" -X utf8 -B - "$SCRIPTS" "$INPUT" "$OUTPUT" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
from land_cex import open_cex
with open_cex(sys.argv[2]) as f:
    print(f.export_csv(sys.argv[3], [16392, 16388]))
PY
```

`wine32 is missing` 表示当前 Wine 安装缺少传统 x86 支持。`Bad EXE format` 或 Windows 错误 193 时，先检查正在运行的 Python 位数和 DLL 架构。`ModuleNotFoundError` 时用上面的 `wine "$PYWIN" -B "$INSTALL_DEPS"` 为同一个解释器安装依赖。
