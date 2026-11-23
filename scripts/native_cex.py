"""Windows SDK bindings and resource lifetime for LANDCex."""

import _deps  # noqa: F401

import ctypes as C
from ctypes import wintypes as W
from contextlib import contextmanager, chdir
import hashlib
import math
import os
from pathlib import Path
import shutil
import tempfile
import uuid


class CexError(Exception):
    def __init__(self, code, message, **details):
        super().__init__(message)
        self.payload = {"code": code, "message": message, **details}


SDK_VERSION = 0x0003030A
DLLS = {
    4: ("x86", "LANDCex_32.dll", "da27a2800bc2f75a0c8bf6c2c7526ab0c58ef7ac5920fcee9d6675b3f4d73c1e"),
    8: ("x64", "LANDCex_x64.dll", "af75c22b0494068df90e3152c1a378ca2e1da1a4dc3fcf9c54b82ca0b1f5663f"),
}
SYS_HASH = "761dcae76898ab25fc17feec13c014d86c3d353536a42acc3cdb3eabeeecb4f4"
CHANNEL_TYPES = ("voltage", "force", "temperature", "pressure", "thickness")


def bind(library, name, result, *arguments):
    fn = getattr(library, name)
    fn.restype = result
    fn.argtypes = arguments
    return fn


def registry_check(code, name):
    if code:
        raise CexError("E_LOAD_FAILED", "Could not isolate the SDK configuration.", native_api=name, native_code=code)


@contextmanager
def isolated_user():
    advapi = C.WinDLL("advapi32")
    key_type = W.HKEY
    key_out = C.POINTER(key_type)
    open_user = bind(advapi, "RegOpenCurrentUser", W.LONG, W.DWORD, key_out)
    create = bind(advapi, "RegCreateKeyExW", W.LONG, key_type, W.LPCWSTR, W.DWORD, W.LPWSTR,
                  W.DWORD, W.DWORD, C.c_void_p, key_out, C.POINTER(W.DWORD))
    override = bind(advapi, "RegOverridePredefKey", W.LONG, key_type, key_type)
    close = bind(advapi, "RegCloseKey", W.LONG, key_type)
    delete = bind(advapi, "RegDeleteTreeW", W.LONG, key_type, W.LPCWSTR)
    current_user = key_type(C.c_int32(0x80000001).value)
    access = 0xF003F  # KEY_ALL_ACCESS
    real_user, isolated = key_type(), key_type()
    disposition = W.DWORD()
    name = "Software\\LANDCexPython-" + uuid.uuid4().hex
    registry_check(open_user(access, C.byref(real_user)), "RegOpenCurrentUser")
    try:
        registry_check(create(real_user, name, 0, None, 1, access, None, C.byref(isolated),
                              C.byref(disposition)), "RegCreateKeyExW")
        try:
            if disposition.value != 1:  # REG_CREATED_NEW_KEY
                raise CexError("E_LOAD_FAILED", "Could not create a private SDK configuration.")
            registry_check(override(current_user, isolated), "RegOverridePredefKey")
            try:
                yield
            finally:
                registry_check(override(current_user, None), "RegOverridePredefKey")
        finally:
            close(isolated)
            if disposition.value == 1:
                registry_check(delete(real_user, name), "RegDeleteTreeW")
    finally:
        close(real_user)


@contextmanager
def native_runtime():
    from _ctypes import FreeLibrary
    try:
        from comtypes import automation
    except ImportError as error:
        raise CexError("E_DEPENDENCY", "Install comtypes for the selected Python interpreter.") from error

    arch, dll_name, dll_hash = DLLS[C.sizeof(C.c_void_p)]
    runtime = Path(__file__).resolve().parents[1] / "runtime" / ("windows-" + arch)
    base = Path(tempfile.gettempdir()).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="land-cex-python-", dir=base) as folder:
        work = Path(folder).resolve(strict=True)
        if work.parent != base:
            raise CexError("E_LOAD_FAILED", "Invalid SDK working directory.")
        for name, expected in ((dll_name, dll_hash), ("LANHE.sys", SYS_HASH)):
            try:
                data = (runtime / name).read_bytes()
            except OSError as error:
                raise CexError("E_DLL_INCOMPATIBLE", f"Packaged SDK dependency is unavailable: {name}.") from error
            if hashlib.sha256(data).hexdigest() != expected:
                raise CexError("E_DLL_INCOMPATIBLE", f"Packaged SDK dependency has an unexpected hash: {name}.")
            (work / name).write_bytes(data)

        kernel = C.WinDLL("kernel32", use_last_error=True)
        get_locale = bind(kernel, "GetThreadLocale", W.DWORD)
        set_locale = bind(kernel, "SetThreadLocale", W.BOOL, W.DWORD)
        old_locale = get_locale()
        if not set_locale(0x0804):
            raise CexError("E_LOAD_FAILED", "Could not set the SDK text locale.", native_api="SetThreadLocale",
                           native_code=C.get_last_error())
        old_env = {key: os.environ.get(key) for key in ("TEMP", "TMP")}
        try:
            os.environ.update(TEMP=str(work), TMP=str(work))
            with chdir(work), isolated_user():
                try:
                    library = C.WinDLL(str(work / dll_name), winmode=0x100 | 0x800)
                except OSError as error:
                    raise CexError("E_DLL_INCOMPATIBLE", str(error), native_api="LoadLibraryExW",
                                   native_code=error.winerror) from error
                try:
                    yield NativeCex(library, work, automation)
                finally:
                    FreeLibrary(library._handle)
        finally:
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            set_locale(old_locale)


class NativeCex:
    def __init__(self, dll, work, automation):
        self.work = work
        self.automation = automation
        self.warning = None
        self.variant = automation.VARIANT
        handle, u32, i32 = C.c_void_p, C.c_uint32, C.c_int32
        vptr = C.POINTER(self.variant)
        check_version = bind(dll, "GetDllVersion", u32)
        if check_version() != SDK_VERSION:
            raise CexError("E_DLL_INCOMPATIBLE", "Unexpected LANDCex SDK version.")
        exports = (
            ("EnableSilentForLoadData", C.c_bool, C.c_bool),
            ("LoadBriefInfo", handle, C.c_char_p),
            ("FreeBriefInfo", None, handle),
            ("LoadData", handle, C.c_char_p, i32),
            ("FreeData", None, handle),
            ("GetLastLoadError", u32, vptr),
            ("GetRows", i32, handle, u32),
            ("GetDataEx", C.c_bool, handle, u32, i32, vptr),
            ("GetStartTime", i32, handle),
            ("GetDescriptionOfMode", C.c_bool, C.c_uint8, vptr),
            ("IsTimeHighResolution", C.c_bool, handle),
            ("GetCycleFromStep", i32, handle, i32),
            ("GetFirstRecOfCycle", i32, handle, i32),
            ("GetLastRecOfCycle", i32, handle, i32),
            ("GetFirstRecOfStep", i32, handle, i32),
            ("GetLastRecOfStep", i32, handle, i32),
            ("GetCycleFromRec", i32, handle, i32, C.POINTER(i32)),
            ("GetFirstChargeStepOfCycle", i32, handle, i32),
            ("GetLastChargeStepOfCycle", i32, handle, i32),
            ("GetBattNo", C.c_bool, handle, vptr),
            ("GetBattBatchNo", C.c_bool, handle, vptr),
            ("GetEndTime", i32, handle),
            ("GetActMaterialMass", C.c_float, handle, C.POINTER(C.c_float)),
            ("GetChannelEx", C.c_bool, handle, C.POINTER(C.c_uint8), C.POINTER(C.c_uint8),
             C.POINTER(u32), C.POINTER(u32)),
            ("GetChlNote", C.c_bool, handle, vptr),
            ("GetDescriptionOfVIRange", C.c_bool, handle, vptr),
            ("GetUnitNameOfColumn", C.c_bool, handle, u32, vptr),
            ("ColumnID_to_Str", C.c_bool, u32, vptr),
            ("GetDescriptionOfColumn", C.c_bool, u32, vptr),
            ("GetDataOfAuxChls", i32, handle, i32, i32, C.POINTER(C.c_float),
             C.POINTER(C.c_int16), C.POINTER(C.c_int16)),
            ("GetDataOfExAuxChls", i32, handle, i32, i32, C.POINTER(C.c_float)),
        )
        for name, result, *arguments in exports:
            try:
                setattr(self, name, bind(dll, name, result, *arguments))
            except AttributeError as error:
                raise CexError("E_DLL_INCOMPATIBLE", f"Missing SDK export: {name}.") from error
        self.EnableSilentForLoadData(True)
        # Supported scalar types returned by the SDK.
        self.scalar_types = {0, 1, 2, 3, 4, 5, 7, 8, 11, 16, 17, 18, 19, 20, 21, 22, 23}

    @contextmanager
    def open(self, source, unit_scheme, *, brief=False):
        with tempfile.TemporaryDirectory(prefix="data-", dir=self.work) as directory:
            staged = Path(directory) / ("input" + source.suffix.lower())
            shutil.copyfile(source, staged)
            path = str(staged.relative_to(self.work)).encode("ascii")
            with self._open_staged(path, unit_scheme, brief) as handle:
                yield handle

    @contextmanager
    def _open_staged(self, path, unit_scheme, brief):
        self.warning = None
        if brief:
            handle = self.LoadBriefInfo(path)
            if handle:
                try:
                    yield handle
                finally:
                    self.FreeBriefInfo(handle)
                return
        handle = self.LoadData(path, unit_scheme)
        try:
            description = self.variant()
            status = self.GetLastLoadError(C.byref(description))
            if not handle:
                raise CexError("E_LOAD_FAILED", "加载失败", native_api="LoadData", native_code=status,
                               native_message=description.value or None)
            if status:
                self.warning = {"native_api": "LoadData", "native_code": status, "message": description.value}
            yield handle
        finally:
            if handle:
                self.FreeData(handle)

    def value(self, function, *arguments):
        variant = self.variant()
        if not function(*arguments, C.byref(variant)):
            return None
        kind = variant.vt
        if kind not in self.scalar_types:
            raise CexError("E_INTERNAL", f"Unsupported SDK value type: {kind}.")
        if kind == self.automation.VT_DATE:
            value = variant._.VT_R8
        elif kind == self.automation.VT_BOOL:
            value = bool(variant.value)
        else:
            value = variant.value
        return None if isinstance(value, float) and not math.isfinite(value) else value

    def count(self, handle, group, channel_type):
        if group == 0:
            return self.GetDataOfAuxChls(handle, 0, channel_type, None, None, None)
        return self.GetDataOfExAuxChls(handle, 0, channel_type, None)

    def file_item(self, handle, item):
        if item in ("start_time", "end_time"):
            api = self.GetStartTime if item == "start_time" else self.GetEndTime
            seconds = api(handle)
            return None if seconds == -1 else seconds
        if item in ("barcode", "batch_no"):
            api = self.GetBattNo if item == "barcode" else self.GetBattBatchNo
            return self.value(api, handle)
        if item == "active_material":
            capacity = C.c_float()
            mass = self.GetActMaterialMass(handle, C.byref(capacity))
            return {"mass_g": mass, "nominal_specific_capacity_mah_g": capacity.value}
        if item == "channel":
            box, channel = C.c_uint8(), C.c_uint8()
            if self.GetChannelEx(handle, C.byref(box), C.byref(channel), None, None):
                return f"{box.value + 1:03d}_{channel.value + 1}"
            return None
        if item in ("channel_note", "vi_range"):
            api = self.GetChlNote if item == "channel_note" else self.GetDescriptionOfVIRange
            return self.value(api, handle)
        group = int(item == "exaux_counts")
        return {name: self.count(handle, group, index) for index, name in enumerate(CHANNEL_TYPES[:4 + group])}

    def rows(self, handle, level_id):
        rows = self.GetRows(handle, level_id)
        if rows < 0:
            raise CexError("E_INTERNAL", "Invalid SDK row count.")
        return rows

    def column(self, handle, field_id, items):
        data = {"id": field_id}
        for item in items:
            if item == "unit":
                data[item] = self.value(self.GetUnitNameOfColumn, handle, field_id)
            else:
                data[item] = self.value(self.GetDescriptionOfColumn, field_id)
        return data
