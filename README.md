# FREERIDE AI 股票研究 DEMO · 消费 V2 / 有色周期增强 V4

在线展示：https://Lancewang1.github.io/freeride-equity-demos/

- [消费：海底捞](https://Lancewang1.github.io/freeride-equity-demos/consumer.html)
- [有色：紫金矿业](https://Lancewang1.github.io/freeride-equity-demos/nonferrous.html)

六步叙事：市场关注点 → 因果逻辑 → 数据证据 → 经营模型及利好/利空裁决 → 共识与价格隐含要求 → 可跟踪结论。

包含研究 HTML、公开公司公告和证据页、研报文献索引、JSON 输入/结果与 Python 复算脚本。经营驱动可交互调整，直接检查是否达到条件盈利门槛。

紫金 V3 从整体金属周期开始，加入 World Bank、FRED、WGC、SGE/SHFE、USGS、已收集的仓单和库存数据，再连接到 Q3 分产品量价成本、项目、现金流与盈利门槛。原有数据的口径纠正和跨源核验随图表数据提供。

紫金新版复算：`python depth_model.py`（仅需 Python 标准库）。输入/输出为 `depth_inputs.json` / `depth_results.json`；图表及核验为 `depth_chart_data.json`；完整 Skill 在 `nonferrous-skill/` 或 `nonferrous-skill.zip`。

原版消费及历史 V2 复算：`python run_demo.py --check` 与 `python narrative_model.py --check`。这些旧脚本不会生成紫金 V3 的新结果。

紫金使用 10-24 披露的 2026Q3 财报；最新 A 股收盘为 10-23（公告前），共识参照仍为 10-20，不能声称股价已反映本次财报。模型以 Q3 扣非为基线，只改变金铜量价成本；赤峰并购尚未完整建模，单独列可编辑调整项。全球铜库存/TC、最新完整共识和逐矿 NAV 输入仍有缺口。

海底捞保留 2026H1 财报及 10-08 市场快照。共识倍数是卖方转引 Bloomberg 表格，EPS 调整定义和样本数未完整披露；由四舍五入 PE 反推的 EPS 仅作条件诊断。海底捞换汇使用 09-30 HKMA 锚，不当作同日汇率。

未包含 API 密钥、内部数据仓库全集或卖方研报原文。公司公告版权归原权利人，原来源见 `sources/source_manifest.json`，新增来源见 `depth_sources.json`，新增原始文件摘要见 `depth_provenance.json`。

## V4 周期增强

2026-10-26 更新框架，事实窗口仍为 10-25。新增周期四问、多维位置仪表、公司资本开支与项目供给、商品/盈利/股价三条时间线、边际需求和结构化判断台账。计算见 `cycle_metrics.json`，未到期监测见 `cycle_ledger.json`。不沿用参考HTML中未核验的行业ROE/分位、确定性顶部结论或概率。
