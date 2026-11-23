"""Stream the three data tables from an already open CEX session."""

import _deps  # noqa: F401
from datetime import datetime
from pathlib import Path

from cex_io import require, target_path
from dt_rows import DURATIONS, RECORD_BOUNDARIES, format_duration


def _write_test_info(workbook, file):
    from openpyxl.cell import WriteOnlyCell
    from openpyxl.styles import Alignment, Font, PatternFill

    info = file.info("barcode", "batch_no", "start_time", "end_time", "active_material", "channel", "vi_range", "channel_note")
    material = info["active_material"]
    mass_mg = material["mass_g"] * 1000
    specific_capacity = material["nominal_specific_capacity_mah_g"]

    def local_time(seconds):
        return datetime.fromtimestamp(seconds) if seconds is not None and seconds > 0 else None

    rows = (
        ("\u7535\u6c60\u6761\u7801", info["barcode"]),
        ("\u7535\u6c60\u6279\u53f7", info["batch_no"]),
        ("\u542f\u52a8\u65f6\u95f4", local_time(info["start_time"])),
        ("\u7ed3\u675f\u65f6\u95f4\uff08\u4f30\u8ba1\uff09", local_time(info["end_time"])),
        ("\u6d3b\u6027\u7269\u8d28\u8d28\u91cf (mg)", mass_mg if mass_mg > 0 else None),
        ("\u6807\u79f0\u6bd4\u5bb9\u91cf (mAh/g)", specific_capacity if specific_capacity > 0 else None),
        ("\u901a\u9053", info["channel"]),
        ("\u7535\u538b\u7535\u6d41\u91cf\u7a0b", info["vi_range"]),
        ("\u901a\u9053\u5907\u6ce8", info["channel_note"]),
    )
    sheet = workbook.create_sheet("\u6d4b\u8bd5\u4fe1\u606f")
    sheet.freeze_panes = "A2"
    sheet.column_dimensions["A"].width = 26
    sheet.column_dimensions["B"].width = 54
    headings = [WriteOnlyCell(sheet, text) for text in ("\u9879\u76ee", "\u503c")]
    for cell in headings:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="2F5597")
    sheet.append(headings)
    for name, value in rows:
        cell = WriteOnlyCell(sheet, value=value)
        if isinstance(value, str):
            cell.data_type = "s"
            cell.alignment = Alignment(wrap_text=True)
        elif isinstance(value, datetime):
            cell.number_format = "yyyy/mm/dd hh:mm:ss"
        elif isinstance(value, float):
            cell.number_format = "0.#######"
        sheet.append([name, cell])
    sheet.close()
    return {"rows": len(rows), "columns": 2}


def export_xlsx(file, output, *, extra_platforms=None, on_row=None, summary_ids=None):
    from openpyxl import Workbook
    from openpyxl.cell import WriteOnlyCell
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter

    target = target_path(output, ".xlsx")
    require(on_row is None or callable(on_row), "on_row must be callable.")
    require(summary_ids is None or on_row is not None, "summary_ids requires on_row.")
    levels = (("cycle", "\u5faa\u73af\u5c42"), ("step", "\u5de5\u6b65\u5c42"), ("rec", "\u8bb0\u5f55\u5c42"))
    workbook = Workbook(write_only=True)
    sdk, handle = file.native
    high_res = sdk.IsTimeHighResolution(handle)
    duration_format = "[h]:mm:ss.000" if high_res else "[h]:mm:ss"
    result = {}
    with file._stage_output(target) as staged:
        try:
            for level, title in levels:
                columns = file.export_columns(level, extra_platforms=extra_platforms)
                rows = file.rows(level)
                require(rows <= 1048575, "Data exceeds the Excel worksheet row limit.", "E_EXPORT_WRITE")
                sheet = workbook.create_sheet(title)
                sheet.freeze_panes = "B2"
                headers = []
                for index, column in enumerate(columns, 1):
                    text = column["header"]
                    minimum_width = 32 if column["id"] == 8194 else 16
                    if column["id"] in RECORD_BOUNDARIES:
                        minimum_width = 22
                    sheet.column_dimensions[get_column_letter(index)].width = max(minimum_width, 3 + sum(1 if c.isascii() else 2 for c in text))
                    cell = WriteOnlyCell(sheet, value=text)
                    cell.data_type = "s"
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill("solid", fgColor="2F5597")
                    headers.append(cell)
                sheet.append(headers)
                ids = [col["id"] for col in columns]
                stream = file.iter_export_rows(level, ids, display_times=False, extra_platforms=extra_platforms,
                                               on_row=on_row if level == "rec" else None,
                                               summary_ids=summary_ids if level == "rec" else None)
                for values in stream:
                    cells = []
                    for field_id, value in zip(ids, values):
                        if value is not None and field_id in DURATIONS:
                            if value >= 0:
                                cell = WriteOnlyCell(sheet, value=value / 86400)
                                cell.number_format = duration_format
                                cells.append(cell)
                                continue
                            value = format_duration(value, field_id, high_res)
                        if isinstance(value, str):
                            cell = WriteOnlyCell(sheet, value=value)
                            cell.data_type = "s"
                            cells.append(cell)
                        else:
                            cells.append(value)
                    sheet.append(cells)
                sheet.close()
                result[level] = {"rows": rows, "columns": len(columns)}
            result["info"] = _write_test_info(workbook, file)
            workbook.save(staged)
        finally:
            for sheet in workbook.worksheets:
                if not sheet.closed:
                    sheet.close()
                # Write-only sheets use temporary XML files until save() consumes them.
                writer = sheet._writer
                if writer is not None and Path(writer.out).is_file():
                    writer.cleanup()
            workbook.close()
    return {"output": str(target), "tables": result}
