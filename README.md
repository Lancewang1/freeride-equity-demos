# FREERIDE AI 股票研究 DEMO · V2

在线展示：https://Lancewang1.github.io/freeride-equity-demos/

- [消费：海底捞](https://Lancewang1.github.io/freeride-equity-demos/consumer.html)
- [有色：紫金矿业](https://Lancewang1.github.io/freeride-equity-demos/nonferrous.html)

六步叙事：市场关注点 → 因果逻辑 → 数据证据 → 经营模型及利好/利空裁决 → 共识与价格隐含要求 → 可跟踪结论。

包含研究 HTML、公开公司公告和证据页、研报文献索引、JSON 输入/结果与 Python 复算脚本。经营驱动可交互调整，直接检查是否达到条件盈利门槛。

复算：`python run_demo.py --check` 与 `python narrative_model.py --check`（仅需 Python 标准库）。

研究使用 2026H1 财报基线；海底捞市场快照为 2026-10-08，紫金为 2026-10-20（10-21 研报披露），未纳入紫金三季报。事实、计算和假设分开标记。共识倍数是卖方转引 Bloomberg 表格，EPS 调整定义和样本数未完整披露；EPS 由四舍五入 PE 反推，盈利口径比较为条件诊断。海底捞换汇使用 09-30 HKMA 有日期的锚，并列敏感性，不能当同日汇率。

未包含 API 密钥、内部数据仓库或卖方研报原文。公司公告版权归原权利人，来源和 SHA256 见 `sources/source_manifest.json`。
