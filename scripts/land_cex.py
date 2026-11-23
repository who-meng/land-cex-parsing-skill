"""Direct Python access to a LANDCex handle owned by a single task."""

import _deps  # noqa: F401

from contextlib import ExitStack, contextmanager
from threading import Lock, get_ident

from cex_io import (BRIEF_ITEMS, FILE_ITEMS, LEVELS, UNITS, check_channels, display_header, excluded_platform_ids,
                    exportable_ids, named_columns, pending_outputs, read_rows, require, selected_fields, source_path,
                    stage_output, target_path, write_csv)
from dt_rows import EXT, SPLIT_SOURCE, extra_columns, table_rows, validate_export_ids
from native_cex import CexError, native_runtime


# The Windows SDK uses process-wide current directory and registry state.
_task_lock = Lock()


class CexFile:
    """Methods are valid on the opening thread, inside open_cex only."""

    def __init__(self, sdk, handle, metadata_only, outputs):
        self._sdk = sdk
        self._handle = handle
        self._metadata_only = metadata_only
        self._pending = outputs.enter_context(pending_outputs())
        self._owner = get_ident()
        self.warning = sdk.warning

    def _check(self, *, full=False):
        require(self._handle is not None and self._owner == get_ident(),
                "Use this file on its opening thread inside open_cex.", "E_SESSION_CLOSED")
        require(not full or not self._metadata_only, "This operation requires a full data handle.")

    @property
    def native(self):
        self._check()
        return self._sdk, self._handle

    def info(self, *items):
        require(items and set(items) <= FILE_ITEMS, "Unknown or missing file information item.")
        self._check(full=not set(items) <= BRIEF_ITEMS)
        return {item: self._sdk.file_item(self._handle, item) for item in items}

    def rows(self, level):
        self._check(full=True)
        require(level in LEVELS, "Unknown table level.")
        return self._sdk.rows(self._handle, LEVELS[level])

    def columns(self, ids):
        self._check(full=True)
        return [self._sdk.column(self._handle, field[0], ("description", "unit"))
                for field in selected_fields(ids)]

    def export_columns(self, level, *, extra_platforms=None):
        """Exportable columns with SDK IDs, filtered by this file's channels."""
        self._check(full=True)
        require(level in LEVELS, "Unknown table level.")
        ids = []
        counts = {}
        excluded = excluded_platform_ids(extra_platforms) if level == "cycle" else set()
        for field_id, _, group, kind, channel in selected_fields(exportable_ids(level)):
            if field_id in excluded:
                continue
            if group >= 0:
                key = (group, kind)
                if key not in counts:
                    counts[key] = self._sdk.count(self._handle, *key)
                if channel > counts[key]:
                    continue
            ids.append(field_id)
        return self._export_descriptions(level, [*ids, *EXT[level]])

    def _export_descriptions(self, level, ids):
        direct = [i for i in ids if i not in EXT[level]]
        deps = [SPLIT_SOURCE[i] for i in ids if i in SPLIT_SOURCE]
        columns = named_columns(self._sdk, self._handle, dict.fromkeys([*direct, *deps]))
        for column in columns:
            column["read_id"] = column["id"]
            column["header"] = display_header(column)
        by_id = {c["id"]: c for c in columns}
        by_id.update((c["id"], c) for c in extra_columns(level, columns))
        return [by_id[i] for i in ids]

    def iter_export_rows(self, level, ids=None, *, start=1, end=None, display_times=True, extra_platforms=None,
                         on_row=None, summary_ids=None):
        """Yield formatted presentation values, including supported derived columns."""
        self._check(full=True)
        if ids is None:
            ids = [column['id'] for column in self.export_columns(level, extra_platforms=extra_platforms)]
        yield from table_rows(self, level, ids, start, end, display_times, extra_platforms, on_row, summary_ids)

    def _selection(self, ids, start, end):
        self._check(full=True)
        fields = selected_fields(ids)
        level = fields[0][1]
        require(all(field[1] == level for field in fields),
                "Expected fields from the same applicable table.", "E_MIXED_LEVEL")
        check_channels(self._sdk, self._handle, fields)
        total = self._sdk.rows(self._handle, level)
        last = total if end is None else end
        require(type(start) is int and type(last) is int and
                ((start == 1 and end is None and total == 0) or 1 <= start <= last <= total),
                "Index out of range.", "E_INVALID_INDEX")
        return [field[0] for field in fields], last

    def iter_rows(self, ids, *, start=1, end=None):
        ids, last = self._selection(ids, start, end)
        values = read_rows(self._sdk, self._handle, ids, start, last)
        for _ in range(start, last + 1):
            self._check()  # A caller may have kept the iterator beyond the context.
            yield next(values)

    def _stage_output(self, target):
        self._check(full=True)
        return stage_output(self._pending, target)

    def export_csv(self, output, ids, *, start=1, end=None, on_row=None, summary_ids=None, display_times=True):
        self._check(full=True)
        target = target_path(output)
        validate_export_ids("rec", ids)
        index = LEVELS["rec"]
        output_ids = [index, *(i for i in ids if i != index)]
        columns = self._export_descriptions("rec", output_ids)
        if on_row is not None and summary_ids is None:
            summary_ids = ids  # Caller order excludes any automatically inserted record number.
        values = self.iter_export_rows("rec", output_ids, start=start, end=end, display_times=display_times,
                                       on_row=on_row, summary_ids=summary_ids)
        with self._stage_output(target) as staged:
            rows = write_csv(staged, columns, values)
        requested = {c["id"]: c for c in columns}
        metadata = [{key: requested[i][key] for key in ("id", "description", "unit")} for i in ids]
        return {"output": str(target.resolve()), "rows": rows, "columns": metadata}


@contextmanager
def _runtime(unit_scheme):
    require(unit_scheme in UNITS, "Unknown unit scheme.")
    require(_task_lock.acquire(blocking=False), "Use one SDK task per Python process.", "E_SESSION_BUSY")
    try:
        with native_runtime() as sdk:
            yield sdk
    finally:
        _task_lock.release()


@contextmanager
def _open_file(sdk, source, unit_scheme, metadata_only):
    with ExitStack() as outputs, sdk.open(source, UNITS[unit_scheme], brief=metadata_only) as handle:
        file = CexFile(sdk, handle, metadata_only, outputs)
        try:
            yield file
        finally:
            file._handle = None


@contextmanager
def open_cex(path, *, unit_scheme="Auto", metadata_only=False):
    source = source_path(path)
    with _runtime(unit_scheme) as sdk, _open_file(sdk, source, unit_scheme, metadata_only) as file:
        yield file


def process_files(paths, process, *, unit_scheme="Auto", metadata_only=False):
    """Return one small result per unique source, with at most one open file."""
    require(callable(process), "Expected a per-file processing function.")
    require(not isinstance(paths, (str, bytes)), "Expected a sequence of file paths.")
    seen = set()
    results = []
    with _runtime(unit_scheme) as sdk:
        for path in paths:
            result = {"file": str(path)}
            try:
                source = source_path(path)
                if source in seen:
                    continue
                seen.add(source)
                result["file"] = str(source)
                with _open_file(sdk, source, unit_scheme, metadata_only) as file:
                    try:
                        data = process(source, file)
                    except (CexError, OSError):
                        raise
                    except Exception as error:
                        raise CexError("E_PROCESS_FAILED", str(error), exception_type=type(error).__name__) from error
                    if file.warning:
                        result["warning"] = file.warning
                result.update(ok=True, data=data)
            except CexError as error:
                result.update(ok=False, error=error.payload)
            except OSError as error:
                result.update(ok=False, error={"code": "E_FILE_IO", "message": str(error)})
            results.append(result)
    return results
