"""Field validation, paths and CSV output for LAND CEX files."""

from contextlib import contextmanager
import csv
from functools import cache
import json
import ntpath
import os
from pathlib import Path
import tempfile

from native_cex import CexError


LEVELS = {"cycle": 4096, "step": 8193, "rec": 16385}
UNITS = {"Auto": -1, "mA": 0, "A": 1, "uA": 2}
BRIEF_ITEMS = {"barcode", "batch_no", "start_time", "end_time", "active_material", "channel", "channel_note", "vi_range"}
FILE_ITEMS = BRIEF_ITEMS | {"aux_counts", "exaux_counts"}


def require(condition, message, code="E_INVALID_REQUEST"):
    if not condition:
        raise CexError(code, message)


def regular_path(raw, suffixes):
    text = os.fspath(raw).replace("/", "\\")
    drive, tail = ntpath.splitdrive(text)
    path = Path(text)
    require(bool(drive) and path.is_absolute() and not text.startswith(("\\\\?\\", "\\\\.\\"))
            and ":" not in tail and "\x00" not in text and not path.is_reserved(),
            "Expected a regular absolute Windows path.")
    require(path.suffix.lower() in suffixes, "Expected file extension " + " or ".join(suffixes) + ".")
    return path


def source_path(raw):
    source = regular_path(raw, (".cex", ".icex"))
    require(source.is_file(), "Input data file does not exist.", "E_INPUT_NOT_FOUND")
    return source.resolve(strict=True)


def target_path(raw, suffix=".csv"):
    target = regular_path(raw, (suffix,))
    require(not os.path.lexists(target), "The output path already exists.", "E_OUTPUT_EXISTS")
    require(target.parent.is_dir(), "The output directory does not exist.", "E_EXPORT_WRITE")
    return target


@cache
def _field_catalog():
    with Path(__file__).with_name("fields.json").open(encoding="ascii") as source:
        return {entry[0]: tuple(entry) for entry in json.load(source)}


def selected_fields(ids):
    require(isinstance(ids, (list, tuple)) and ids, "Expected a nonempty list of field IDs.")
    require(all(type(value) is int and 0 <= value < 2**32 for value in ids), "Expected an unsigned numeric field ID.")
    require(len(set(ids)) == len(ids), "Duplicate field ID.")
    catalog = _field_catalog()
    for field_id in ids:
        require(field_id in catalog, f"Unknown field ID: {field_id}.", "E_UNKNOWN_COLUMN")
    return [catalog[field_id] for field_id in ids]


def check_channels(sdk, handle, fields):
    seen = (set(), set())
    for _, _, group, channel_type, channel in fields:
        if group < 0 or (channel_type, channel) in seen[group]:
            continue
        seen[group].add((channel_type, channel))
        require(channel <= sdk.count(handle, group, channel_type), "Channel is not bound.", "E_CHANNEL_UNBOUND")


def read_rows(sdk, handle, ids, first, last):
    for number in range(first, last + 1):
        yield [sdk.value(sdk.GetDataEx, handle, field_id, number - 1) for field_id in ids]


def csv_cell(value):
    if isinstance(value, str) and value.lstrip().startswith(tuple("=+-@＝＋－＠")):
        return "'" + value
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


@cache
def exportable_ids(level):
    with Path(__file__).with_name("dt-export-ranges.json").open(encoding="ascii") as source:
        ranges = json.load(source)[level]
    return tuple(field_id for first, last in ranges for field_id in range(first, last + 1))


# First slot of each capacity, specific capacity, percentage and time series.
_PLATFORM_BASES = {"discharge": (4608, 4624, 4640, 4656), "charge": (4672, 4688, 4704, 4720)}


def excluded_platform_ids(extra_platforms):
    extra = {} if extra_platforms is None else extra_platforms
    require(isinstance(extra, dict) and extra.keys() <= _PLATFORM_BASES.keys(),
            "Expected extra platform slots keyed by charge or discharge.")
    excluded = set()
    for direction, bases in _PLATFORM_BASES.items():
        slots = extra.get(direction, ())
        require(isinstance(slots, (list, tuple)) and all(type(i) is int and 3 <= i <= 5 for i in slots),
                "Confirmed extra platform slots must be 3, 4 or 5.")
        for slot in range(3, 6):
            if slot not in slots:
                excluded.update(base + slot - 1 for base in bases)
    return excluded


def display_header(column):
    name, unit = column["description"], column["unit"]
    return f"{name} ({unit})" if unit else name


def named_columns(sdk, handle, ids):
    columns = []
    for field_id in ids:
        column = sdk.column(handle, field_id, ("description", "unit"))
        if not column["description"]:
            column["description"] = sdk.value(sdk.ColumnID_to_Str, field_id)
        require(column["description"], f"No SDK name for field {field_id}.", "E_COLUMN_NAME")
        columns.append(column)
    return columns


@contextmanager
def pending_outputs():
    pending = {}
    published = []
    try:
        yield pending
        for target, staged in pending.items():
            try:
                os.rename(staged, target)  # Same-volume Windows rename refuses an existing target.
            except OSError as error:
                code = "E_OUTPUT_EXISTS" if isinstance(error, FileExistsError) else "E_EXPORT_WRITE"
                raise CexError(code, str(error), failed_output=str(target), published_outputs=published.copy()) from error
            published.append(str(target))
    finally:
        for staged in pending.values():
            staged.unlink(missing_ok=True)


@contextmanager
def stage_output(pending, target):
    key = target.resolve()
    require(key not in pending, "Duplicate output path in this task.", "E_OUTPUT_EXISTS")
    with tempfile.NamedTemporaryFile(dir=key.parent, prefix=".land-cex-", suffix=".tmp", delete=False) as stream:
        staged = Path(stream.name)
    pending[key] = staged
    try:
        yield staged
    except BaseException:
        pending.pop(key)
        staged.unlink(missing_ok=True)
        raise


def write_csv(staged, columns, rows):
    count = 0
    with staged.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow([csv_cell(display_header(col)) for col in columns])
        for row in rows:
            writer.writerow([csv_cell(value) for value in row])
            count += 1
    return count
