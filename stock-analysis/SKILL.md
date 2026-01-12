---
name: stock-analysis
description: 股票数据获取与技术分析框架，集成 LongPort API 实现自选清单管理、多周期 K 线数据获取与完整技术指标计算。适用于需要实时行情数据、技术面分析的量化交易、策略回测、个股研究等场景。
---

## 核心功能

stock-analysis 提供两层能力，构成完整的股票分析工作流：

### 1. 自选清单管理 (`longport_groups.py`)
- 创建、查看、修改、删除监视分组
- 批量管理股票符号，支持增删改
- 导出分组成员列表，供后续数据获取使用

### 2. K 线数据获取与技术分析 (`longport_candlesticks.py`)
- 支持 5 分钟至月线多个周期
- 返回 pandas DataFrame，包含 OHLCV 数据
- 集成 40+ 技术指标计算（EMA、MACD、RSI、ATR、BBANDS 等）
- 支持前复权调整，CSV 导出
- 指标计算由内部完成，无需用户干预

## 典型工作流

```
1. list_groups()          → 列出所有自选分组
2. get_symbols()          → 获取特定分组的股票列表
3. fetch_candlesticks()   → 拉取每只股票的 K 线数据
4. compute_full_suite()   → 计算完整技术指标
5. export to CSV          → 导出分析结果供策略使用
```

## 使用场景

- **量化交易**：获取历史数据与技术指标用于策略开发和回测
- **个股研究**：快速计算技术面数据，支持多周期对比分析
- **筛选监视**：定期计算自选清单的关键指标，发现交易信号
- **数据整理**：批量导出标准格式的 OHLCV + 指标数据

## 快速开始

详见 [快速开始指南](references/quick_start.md) 了解端到端示例。

核心工作流说明见 [API 工作流概览](references/api_workflow.md)。

技术指标详解见 [指标参考](references/indicator_reference.md)。