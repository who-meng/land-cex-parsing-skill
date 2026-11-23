"""Default duration display and fields computed from the live LANDCex handle."""
import ctypes
from functools import lru_cache

from cex_io import LEVELS, display_header, excluded_platform_ids, exportable_ids, require, selected_fields

# Derived column IDs belong to the exporter, not the native SDK.
STEP_CYCLE, STEP_START = 0x2801, 0x2802
REC_CYCLE, REC_STEP, REC_STATE, CAP_C, CAP_D, ENERGY_C, ENERGY_D = range(0x4802, 0x4809)
# Skill-defined IDs above the native 16-bit column namespace.
CYCLE_START, CYCLE_END, STEP_END = 0x11001, 0x11002, 0x12001
RECORD_BOUNDARIES = {CYCLE_START: "GetFirstRecOfCycle", CYCLE_END: "GetLastRecOfCycle",
                     STEP_START: "GetFirstRecOfStep", STEP_END: "GetLastRecOfStep"}
EXT = {"cycle": {CYCLE_START: "\u5faa\u73af\u5f00\u59cb\u65f6\u95f4", CYCLE_END: "\u5faa\u73af\u7ed3\u675f\u65f6\u95f4"},
       "step": {STEP_CYCLE: "\u5faa\u73af\u5e8f\u53f7", STEP_START: "\u5de5\u6b65\u5f00\u59cb\u65f6\u95f4", STEP_END: "\u5de5\u6b65\u7ed3\u675f\u65f6\u95f4"},
       "rec": {REC_CYCLE: "\u5faa\u73af\u5e8f\u53f7", REC_STEP: "\u5de5\u6b65\u5e8f\u53f7", REC_STATE: "\u5de5\u6b65\u72b6\u6001",
               CAP_C: "\u5145\u7535\u5bb9\u91cf", CAP_D: "\u653e\u7535\u5bb9\u91cf", ENERGY_C: "\u5145\u7535\u80fd\u91cf", ENERGY_D: "\u653e\u7535\u80fd\u91cf"}}
SPLIT_SOURCE = {CAP_C: 16389, CAP_D: 16389, ENERGY_C: 16393, ENERGY_D: 16393}
# Default record state abbreviations.
STATE = {0x02:"CCD", 0x03:"CCC", 0x04:"CVD", 0x05:"CVC", 0x13:"CPD", 0x14:"CPC", 0x15:"CRC", 0x16:"CRD",
         0x1a:"DCIR", 0x70:"R", 0x72:"CCVC_D", 0x73:"CCVC_C", 0x74:"S", 0x75:"RateD", 0x76:"RateC",
         0x77:"PAUSE", 0x79:"R", 0x7f:"IncubLink"}
DURATIONS = frozenset((4122, 4123, 8195, 16386, 16387, *range(4656,4661), *range(4720,4725)))


def format_duration(seconds, field_id, high_resolution):
    if seconds is None:
        return None
    magnitude = abs(seconds)
    rounded = magnitude + (0.0005 if high_resolution else 0.5)
    whole = int(rounded)
    hours, remainder = divmod(whole, 3600)
    minutes, sec = divmod(remainder, 60)
    sign = "-" if seconds < 0 and magnitude >= 0.0005 else ""
    days = ""
    if field_id == 16386 and hours >= 24:
        day_count, hours = divmod(hours, 24)
        days = f"{day_count}-"
    fractional = f".{int((rounded-whole)*1000):03d}" if high_resolution else ""
    return f"{sign}{days}{hours:02d}:{minutes:02d}:{sec:02d}{fractional}"


def display_formatter(sdk, handle, ids, display_times=True):
    """Share default duration and step-mode presentation across read/export paths."""
    time_ids = set(ids).intersection(DURATIONS) if display_times else set()
    high_res = bool(time_ids) and sdk.IsTimeHighResolution(handle)

    @lru_cache(maxsize=256)
    def mode_name(code):
        return sdk.value(sdk.GetDescriptionOfMode, code) if code is not None else None

    def format_row(row):
        result = []
        for field_id, value in zip(ids, row):
            if field_id == 8194:
                value = mode_name(value)
            elif field_id in time_ids:
                value = format_duration(value, field_id, high_res)
            result.append(value)
        return result

    return format_row


def extra_columns(level, direct):
    units = {c['id']: c['unit'] for c in direct}
    for field, title in EXT[level].items():
        column = dict(id=field, read_id=None, description=title, unit=units.get(SPLIT_SOURCE.get(field), ''))
        column['header'] = display_header(column)
        yield column


def validate_export_ids(level, ids):
    require(level in LEVELS, 'Unknown table level.')
    require(isinstance(ids, (list, tuple)) and ids and all(type(i) is int for i in ids) and len(set(ids)) == len(ids),
            'Expected distinct numeric column IDs.')
    allowed = set(exportable_ids(level)).union(EXT[level])
    for field in ids:
        require(field in allowed, f'Column {field} is outside the {level} export table.', 'E_NOT_EXPORTABLE')


def table_rows(file, level, ids, start, end, display_times, extra_platforms, on_row=None, summary_ids=None):
    sdk, h = file.native
    validate_export_ids(level, ids)
    ext = EXT[level]
    if level == 'cycle':
        require(excluded_platform_ids(extra_platforms).isdisjoint(ids),
                'Confirm the direction and extra platform slots before exporting them.', 'E_PLATFORM_CONFIRMATION')
    require(on_row is None or (level == 'rec' and callable(on_row)), 'Expected a record row callback.')
    require(summary_ids is None or on_row is not None, 'summary_ids requires on_row.')
    observed = []
    if on_row is not None:
        observed = ids if summary_ids is None else summary_ids
        require(isinstance(observed, (list, tuple)) and observed and all(type(i) is int for i in observed)
                and len(set(observed)) == len(observed), 'Expected distinct summary IDs.')
    observed_native = [i for i in observed if i not in ext]
    if observed_native:
        require(all(f[1] == LEVELS['rec'] for f in selected_fields(observed_native)),
                'Expected record summary fields.', 'E_MIXED_LEVEL')
    direct = [i for i in ids if i not in ext and i != LEVELS[level]]
    wanted = set(ids).union(observed).intersection(ext)
    splits = wanted.intersection(SPLIT_SOURCE)
    sources = list(dict.fromkeys([*direct, *observed_native, *(SPLIT_SOURCE[i] for i in splits)]))
    sources = sources or [LEVELS[level]]
    boundaries = [(i, getattr(sdk, RECORD_BOUNDARIES[i])) for i in ids if i in RECORD_BOUNDARIES]
    splits = wanted.intersection(SPLIT_SOURCE)
    format_row = display_formatter(sdk, h, ids, display_times)

    @lru_cache(maxsize=1)
    def charge_range(cycle):
        return sdk.GetFirstChargeStepOfCycle(h, cycle), sdk.GetLastChargeStepOfCycle(h, cycle)

    @lru_cache(maxsize=1)
    def step_state(step):
        mode = sdk.value(sdk.GetDataEx, h, 8194, step)
        return STATE.get(mode) if mode is not None else None

    step_end = -1
    for index, row in enumerate(file.iter_rows(sources, start=start, end=end), start-1):
        raw = dict(zip(sources, row))
        values = {i:raw[i] for i in direct}
        if LEVELS[level] in ids:
            values[LEVELS[level]] = index + 1
        for field_id, locate in boundaries:
            record = locate(h, index)
            values[field_id] = sdk.value(sdk.GetDataEx, h, 16395, record) if record >= 0 else None
        if STEP_CYCLE in wanted:
            cycle = sdk.GetCycleFromStep(h, index)
            values[STEP_CYCLE] = cycle+1 if cycle >= 0 else None
        elif wanted and level == 'rec':
            if index > step_end:
                step_out = ctypes.c_int32(-1)
                cycle = sdk.GetCycleFromRec(h, index, ctypes.byref(step_out))
                step = step_out.value
                step_end = sdk.GetLastRecOfStep(h, step) if step >= 0 and cycle >= 0 else index
            values[REC_CYCLE] = cycle+1 if cycle >= 0 else None
            values[REC_STEP] = step+1 if step >= 0 else None
            if REC_STATE in wanted:
                values[REC_STATE] = step_state(step) if step >= 0 else None
            if splits:
                if cycle < 0 or step < 0:
                    values.update(dict.fromkeys(splits))
                else:
                    first, last = charge_range(cycle)
                    charging = first <= step <= last
                    for field_id in splits:
                        active = charging == (field_id in (CAP_C, ENERGY_C))
                        values[field_id] = raw[SPLIT_SOURCE[field_id]] if active else 0
        if on_row is not None:
            on_row(index + 1, tuple(values[i] if i in ext else raw[i] for i in observed))
        yield format_row([values[i] for i in ids])
