# 动态通道

使用 `data.info("aux_counts", "exaux_counts")` 查询当前文件的实际绑定数。内部组和外部组均返回 `voltage`（辅压）、`force`（压力）、`temperature`（辅温）、`pressure`（液压），外部组另有 `thickness`（厚度）。

按组、类型和类型内从 1 起的序号在[字段表](fields.md)选 ID。例如已绑定五路内部辅温，可选择 `Rec.AuxTemp05`。Python 会话可同时读取或导出全部已绑定通道。绑定存在时个别行仍可能缺值。

循环平台槽位需要结合配置解释。实测零和 SDK 对未配置槽位返回的零均原样保留。
