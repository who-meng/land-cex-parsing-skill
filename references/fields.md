# 字段目录

以下目录列出支持的字段 ID、名称与中文表头。实际可用字段由 DLL 能力和当前文件的通道配置决定。

共 **1985 个当前字段**，覆盖 12 个映射表；保留标识和旧 ID 别名不计入字段数。

## 按子表查找

| 子表 | 字段数 | 完整 ID／名称／中文表头 |
|---|---:|---|
| `Cycle.` | 903 | [Cycle 字段表](fields-cycle.md) |
| `Step.` | 856 | [Step 字段表](fields-step.md) |
| `Rec.` | 226 | [Rec 字段表](fields-rec.md) |

请求使用十进制数字 ID。请从对应层级表选取 DLL 已识别的 ID。动态通道还须核对当前文件的实际绑定数。名称用于查表。

字段选择不受单独的导出范围限制。读取使用目录中的原生 SDK ID；此技能不另设组合列 ID。需要循环/工步归属时调用 DLL 关联接口，由任务代码决定如何使用结果。

## 动态通道

在活动详细句柄内，用 `sdk.GetDataOfAuxChls(handle, 0, kind, None, None, None)` 查询内部辅助通道数，或 `sdk.GetDataOfExAuxChls(handle, 0, kind, None)` 查询外部辅助通道数。`kind=0/1/2/3/4` 依次表示 `voltage`（辅压）、`force`（压力）、`temperature`（辅温）、`pressure`（液压），以及仅外部组支持的 `thickness`（厚度）。

按组、类型和类型内从 1 起的序号在[字段表](fields.md)选 ID。例如已绑定五路内部辅温，可选择 `Rec.AuxTemp05`。可读取全部已绑定通道；调用 `sdk.check_column(handle, column_id)` 检查指定通道是否绑定。绑定存在时个别行仍可能缺值。

循环平台槽位需要结合配置解释。实测零和 SDK 对未配置槽位返回的零均原样保留。
