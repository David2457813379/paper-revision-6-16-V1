# Optional QA Tools

本目录中的脚本是可选质量检查工具，不属于论文复现的主运行链路。论文代码的正式复现流程仍然是按顺序运行四个 Notebook：

1. `experiment_code/notebooks/01_Parametric_Simulation_Database_Construction.ipynb`
2. `experiment_code/notebooks/02_SRC_Sensitivity_and_Variable_Selection.ipynb`
3. `experiment_code/notebooks/03_ML_Model_Training_and_Evaluation.ipynb`
4. `experiment_code/notebooks/04_EUI_OCEI_Coupling_and_Carbon_Analysis.ipynb`

## `check_repository_quality.py`

用途：在不执行 Notebook 的情况下做静态质量检查，重点防止投稿版常见小错误再次出现。

检查内容：

- 四个 Notebook 的代码单元是否存在语法错误。
- 代码单元是否残留中文图表文本、全角符号、特殊 dash、上标字符或中点单位符号。
- 四个 Notebook 是否错误导入了可选 `tools`，从而破坏“只运行四个 Notebook”的主流程。
- `outputs_step1/` 至 `outputs_step4/` 和 `paper_assets/` 中的 CSV、TXT、SVG、JSON、MD 是否残留中文字符。

运行方式：

```bash
python tools/check_repository_quality.py
```

## `validate_notebooks.py`

用途：按 `01 -> 02 -> 03 -> 04` 顺序实际执行四个 Notebook，确认当前代码在本地 Jupyter/Python 环境下可以完整跑通。

快速验证模式会使用较小样本并跳过 EnergyPlus 仿真，适合每次修改代码后确认 Python 逻辑、绘图、文件读写和跨 Notebook 依赖没有报错：

```bash
python tools/validate_notebooks.py --fast --samples 200
```

如需允许 EnergyPlus 参与验证，可显式打开：

```bash
python tools/validate_notebooks.py --fast --samples 200 --run-energyplus
```

完整复现实验仍建议直接在 Jupyter 中运行四个 Notebook，并在 Notebook 配置中设置：

```python
CONFIG["n_samples"] = 20000
CONFIG["run_energyplus"] = True
```

验证日志会写入：

```text
archive/validation/
```

`archive/` 默认不纳入 Git 版本控制，因此这些日志仅作为本地调试证据保留。
