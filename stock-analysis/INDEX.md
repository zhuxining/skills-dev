# stock-analysis 技能资源地图

## 概述

stock-analysis 是一个完整的股票分析框架，包含两个核心脚本和详细的参考文档。本文件描述如何使用各项资源。

---

## 📚 文件结构

```
stock-analysis/
├── SKILL.md                    # 技能元数据和核心说明
├── INDEX.md                    # 资源导航地图（本文件）
├── scripts/                    # 可执行脚本
│   ├── longport_groups.py     # 自选清单管理
│   ├── longport_candlesticks.py # K线数据获取 + 指标计算
│   ├── talib_calculator.py    # 内部指标计算库（不直接调用）
│   ├── pyproject.toml         # 项目依赖配置
│   └── AGENTS.md              # 脚本编写规范
├── references/                 # 参考文档（按需加载）
│   ├── api_workflow.md        # API 工作流概览与脚本总览
│   ├── groups_management.md   # 自选清单管理完全指南
│   ├── candlesticks_guide.md  # K线数据获取与量化规则应用
│   └── indicator_reference.md # 40+ 技术指标详解
├── assets/                     # 输出资源
│   ├── csv_template.md        # CSV 导出格式规范
│   └── sample_analysis_output.csv # 示例输出文件
└── input/                      # 测试数据（预留）

```

---

## 📖 文档导航

### 新手快速入门
**读者**: 首次使用 stock-analysis，想快速上手  
**推荐路径**:
1. [SKILL.md](SKILL.md) - 了解核心功能和工作流（5 分钟）
2. [quick_start.md](references/quick_start.md) - 跟随 5 个实际场景学习（15 分钟）
3. 运行其中一个示例，获得第一个分析结果

### API 和集成开发
**读者**: 集成 stock-analysis 到自己的系统或开发扩展  
**推荐路径**:
1. [SKILL.md](SKILL.md) - 理解两层架构（自选清单 + K线数据）
2. [api_workflow.md](references/api_workflow.md) - 快速查看工作流概览
3. 选择适用的深入指南:
   - 需要管理自选清单 → [groups_management.md](references/groups_management.md)
   - 需要获取数据并应用量化规则 → [candlesticks_guide.md](references/candlesticks_guide.md)
4. [csv_template.md](assets/csv_template.md) - 了解输出数据格式

### 技术指标分析
**读者**: 需要深入理解某个或多个技术指标  
**推荐路径**:
1. [indicator_reference.md](references/indicator_reference.md) - 查找指标分类、计算原理、应用场景
2. [candlesticks_guide.md](references/candlesticks_guide.md) 中的量化规则示例 - 学习如何应用指标

---

## 🔍 核心脚本快速查表

### `longport_groups.py` - 自选清单管理

| 功能 | 命令 | 输出 |
|------|------|------|
| 列出清单 | `uv run ... list` | 表格（ID、名称、成员数） |
| 创建清单 | `uv run ... create --name "..." --symbols ...` | 创建成功提示 |
| 添加成员 | `uv run ... update --id ... --add-symbols ...` | 更新成功提示 |
| 导出成员 | `uv run ... get-symbols --id ... --output ...` | 纯文本或 CSV 文件 |
| 删除清单 | `uv run ... delete --id ...` | 删除成功提示 |

**详见**: [groups_management.md](references/groups_management.md) - 完整 CLI 参考和工作流示例

---

### `longport_candlesticks.py` - K线数据获取与指标计算

| 功能 | 命令示例 | 输出 |
|------|--------|------|
| 获取日线 OHLCV | `uv run ... --symbol 700.HK --period day --count 100` | CSV (OHLCV) |
| 添加技术指标 | `... --indicators ema,macd,rsi,atr,bbands` | CSV (OHLCV + 指标) |
| 选择特定指标 | `... --indicators ema,rsi` | CSV (仅包含选中指标) |
| 其他周期 | `--period 5m`, `4h`, `week`, `month` | 同上格式 |
| 导出到文件 | `... --output output/700.csv` | CSV 文件 |

**支持周期**: 5m, 10m, 15m, 30m, 60m, 120m, 1h, 4h, day, week, month  
**支持的指标**: ema, macd, adx, rsi, cci, stoch, atr, bbands, obv, ad, volume_sma, vwma, change, mid_price

**详见**: [candlesticks_guide.md](references/candlesticks_guide.md) - 包含 4 个量化规则应用示例（EMA 交叉、RSI 超卖、MACD 多层规则、批量评估）

---

### `talib_calculator.py` - 内部指标计算库

此脚本由 `longport_candlesticks.py` 内部调用，**用户无需直接使用**。指标通过 `--indicators` 参数自动计算。

**详见**: [api_workflow.md](references/api_workflow.md) 的"脚本总览"部分

---

## 🎯 常见任务

### 任务 1: 获取某只股票的当日技术面数据

**场景**: 研究腾讯 (700.HK) 的今日表现  
**步骤**:
1. 执行命令获取最新 K 线数据 + 常用指标
2. 查看 EMA、MACD、RSI 等关键指标
3. 参考 [indicator_reference.md](references/indicator_reference.md) 理解指标含义

**代码**: [quick_start.md - 场景 1](references/quick_start.md#场景-1-获取特定股票的日线数据与技术指标)

---

### 任务 2: 批量获取自选清单的数据

**场景**: 定期计算自选股票的所有指标，用于选股  
**步骤**:
1. 使用 `longport_groups.py` 导出自选清单
2. 为每只股票获取数据 + 指标
3. 合并结果供进一步分析

**代码**: [quick_start.md - 场景 2](references/quick_start.md#场景-2-批量获取自选清单中的股票数据)

---

### 任务 3: 创建并管理自定义分组

**场景**: 建立"美股龙头"分组，快速跟踪核心持仓  
**步骤**:
1. 使用 `create` 命令创建分组
2. 使用 `update` 命令添加/删除成员
3. 使用 `get-symbols` 导出成员列表

**代码**: [quick_start.md - 场景 3](references/quick_start.md#场景-3-创建新的自选清单并管理成员)

---

### 任务 4: 批量获取自定义指标

**场景**: 仅需要特定几个指标，减少计算时间  
**步骤**:
1. 通过 `--indicators` 参数指定所需指标
2. 为多只股票批量获取数据
3. 合并结果供进一步分析

**代码**: [quick_start.md - 场景 4](references/quick_start.md#场景-4-批量获取自定义指标组合)

### 任务 5: 应用量化规则进行信号生成

**场景**: 自动检测 EMA 交叉、RSI 超卖等交易信号  
**步骤**:
1. 获取最新 N 条 K 线数据（参考 [candlesticks_guide.md](references/candlesticks_guide.md)）
2. 计算所需指标（EMA、MACD、RSI 等）
3. 应用量化规则生成买卖信号
4. 参考 [indicator_reference.md](references/indicator_reference.md) 理解指标原理

**代码**: [candlesticks_guide.md - 量化规则应用示例](references/candlesticks_guide.md#量化规则应用示例) - 包含 4 个完整量化规则示例

---

### CSV 输出格式
- **标准列**: symbol, datetime, open, high, low, close, volume, turnover
- **指标列**: 按照 [csv_template.md](assets/csv_template.md) 规范
- **编码**: UTF-8，日期 ISO 8601 格式
- **示例文件**: [sample_analysis_output.csv](assets/sample_analysis_output.csv)

**详见**: [csv_template.md](assets/csv_template.md)

---

## ⚙️ 配置和环境

### 依赖管理
- 各脚本使用 PEP 723 声明依赖，通过 `uv run` 自动解析
- 主要依赖: `longport`, `pandas`, `ta-lib`

**详见**: [scripts/pyproject.toml](scripts/pyproject.toml)

### 环境变量
- LongPort API 认证通过 `.env` 文件配置
- 需要: `LONGPORT_APP_KEY`, `LONGPORT_APP_SECRET`, `LONGPORT_ACCESS_TOKEN`

**详见**: [api_workflow.md - 环境配置](references/api_workflow.md#环境配置)

---

## 🔗 技能内部跨引用

- **SKILL.md** → 引导用户到 quick_start.md, indicator_reference.md, api_workflow.md
- **quick_start.md** → 包含 5 个场景，每个场景都引用其他参考文档
- **api_workflow.md** → 详细说明三个脚本的 API，引用 indicator_reference.md 了解指标
- **indicator_reference.md** → 完整指标库，不依赖其他文档但在 api_workflow.md 中被引用
- **csv_template.md** → 数据格式规范，被 api_workflow.md 和 quick_start.md 引用
- **sample_analysis_output.csv** → 示例数据，对应 csv_template.md 的说明

---

## 📞 常见问题

### Q: 我不知道从哪里开始？
A: 从 [SKILL.md](SKILL.md) 了解核心功能，然后跟随 [quick_start.md](references/quick_start.md) 中的 5 个场景学习。

### Q: 如何理解某个技术指标？
A: 查看 [indicator_reference.md](references/indicator_reference.md)，按指标名称或大类查找。

### Q: CSV 输出的列是什么意思？
A: 参考 [csv_template.md](assets/csv_template.md)，该文件详细说明每个列的含义和精度。

### Q: 我想扩展或修改脚本，有什么规范吗？
A: 查看 [scripts/AGENTS.md](scripts/AGENTS.md)，了解 PEP 723、文档、错误处理等规范。

### Q: 如何集成到我自己的系统？
A: 阅读 [api_workflow.md](references/api_workflow.md) 了解各模块的 API 和数据格式，参考 [quick_start.md](references/quick_start.md) 中的 Python 脚本示例。

---

## 📝 版本和更新

| 版本 | 日期 | 内容 |
|------|------|------|
| 1.0 | 2026-01-12 | 初版发布，包含 3 个脚本和完整文档 |

---

## 📖 许可和使用

stock-analysis 作为 skills-dev 项目的一部分，遵循项目总体许可协议。各脚本依赖的开源库请参考相应 LICENSES。

