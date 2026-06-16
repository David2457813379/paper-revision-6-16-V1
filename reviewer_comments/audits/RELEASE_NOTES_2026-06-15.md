# 论文修改项目 — 版本发布

## Release: 2026-06-15

### 修改内容
- 修复全部4个Jupyter Notebook的语法错误
- 移除 `from __future__ import annotations` 导致的路径求值失败
- 修正变量命名不一致（room_num→room_count, shgc_south→shgc_s）
- 修复图片文字重叠问题，统一matplotlib参数
- 添加中文字体自动检测支持
- 生成酒店建筑工程示意图（3张）
- 生成完整管道13张发表级图表
- 重建116样本仿真数据集
- 编写研究复现README（12KB）
- 集成GitHub顶级AI学术技能包（academic-research-skills + nature-skills）
- 更新CLAUDE.md项目配置

### 文件版本标注
每个文件标注了最后修改日期（2026-06-15），详见 VERSION_MANIFEST.txt

### 第二轮审稿修订加固（2026-06-15）

- 四个 Notebook 已逐一插入中英文双语 Cell 说明；每个代码 Cell 前均有中文解释和英文解释，覆盖目的、输入、方法、输出和审稿意见对应关系。
- NB01 修复可行性筛选覆盖图的索引逻辑，保留原始 LHS 索引，并新增逐变量筛选前后 KS 统计量和 Jensen-Shannon 距离输出。
- NB01 将 `n_samples`、是否运行 EnergyPlus、清理输出目录等设置改为环境变量控制，避免快速验证时误删历史仿真目录。
- NB02 新增快速模式参数，降低验证时 bootstrap 和 SHAP 训练成本；保留正式模式下的完整 bootstrap 与 XGBoost-SHAP 分析。
- NB03 重构模型训练返回值，保存全部模型的搜索对象、最终超参数和搜索空间；修复超参数提取对 Pipeline、GridSearchCV 和 RandomizedSearchCV 的兼容性。
- NB03 补充 18 个关键变量与全变量模型性能对比，用于检验非核心变量固定是否虚高模型性能。
- NB04 调整排放因子敏感性分析顺序，确保在 OCEI 数据构建之后执行；补充电力脱碳情景下各能源载体碳贡献份额。
- NB04 修复 OCEI 建模前的缺失值过滤和能源列数值清洗，避免快速复现数据中出现 NaN target。
- NB04 合并原碳贡献绝对值图和归一化图，生成 `carbon_contribution_dual_view.png`，回应图表冗余意见。
- 使用 `nbclient` 干净内核顺序执行四个 Notebook，快速验证模式全部通过：`EUI_FAST_MODE=1`、`EUI_N_SAMPLES=120`、`EUI_RUN_ENERGYPLUS=0`。
- 新增 `REVIEWER_REVISION_AUDIT_2026-06-15.md`，按 P0-P3 风险等级整理审稿意见、科研关键性、代码修改证据、验证状态和剩余限制。
