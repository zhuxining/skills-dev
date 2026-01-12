# API 工作流概览

stock-analysis 包含两个核心脚本，负责股票分析的数据管道：

1. **自选清单管理** - 创建和维护股票分组
2. **K线数据获取与分析** - 获取最新数据并应用量化规则

## 数据流架构

```
LongPort API
    ↓
longport_groups.py (管理分组)
    ↓
导出符号列表
    ↓
longport_candlesticks.py (获取 K 线数据 + 计算指标)
    ↓
应用量化规则 (indicator_reference.md)
    ↓
生成分析结果
```

## 详细指南

### [自选清单管理指南](groups_management.md)

掌握如何：
- 创建和维护分组（watchlist groups）
- 添加/删除/替换分组成员
- 导出符号列表供数据获取使用

**适用场景**: 
- 整理投资组合
- 组织不同策略的股票
- 定期维护监视清单

### [K线数据获取与量化规则应用指南](candlesticks_guide.md)

掌握如何：
- 获取最新 N 条 K 线数据
- 计算技术指标（EMA、MACD、RSI 等）
- 应用量化规则进行分析

**包含示例**:
- EMA 均线交叉策略
- RSI 超卖买入信号
- MACD 趋势确认
- 批量股票评估

**适用场景**:
- 日常技术分析
- 量化规则开发和应用
- 批量股票筛选

## 技术指标参考

所有支持的技术指标的详细说明（计算原理、应用场景、参数配置），见:

**[技术指标参考](indicator_reference.md)**

## 脚本总览

### longport_groups.py - 自选清单管理

**位置**: `stock-analysis/scripts/longport_groups.py`

**功能**: 创建、维护和导出 LongPort 监视分组。

**主要命令**:
```bash
list                # 列出所有分组
create              # 创建新分组
update              # 修改分组成员
get-symbols         # 导出分组成员
delete              # 删除分组
```

**详细用法**: [自选清单管理指南](groups_management.md)

---

### longport_candlesticks.py - K线数据获取

**位置**: `stock-analysis/scripts/longport_candlesticks.py`

**功能**: 从 LongPort API 获取最新 N 条 K 线数据，支持多周期和技术指标计算。

**主要参数**:
- `--symbol`: 股票代码（必需），如 `700.HK`, `AAPL.US`
- `--period`: K 线周期（默认 day），支持 5m ~ month
- `--count`: 返回数据条数（默认 100）
- `--indicators`: 技术指标列表（可选），如 `ema,macd,rsi,atr,bbands`
- `--output`: 输出文件路径（可选）

**快速示例**:
```bash
# 获取日线数据
uv run longport_candlesticks.py --symbol 700.HK --period day --count 100

# 获取数据并计算指标
uv run longport_candlesticks.py --symbol 700.HK --period day --count 200 \
    --indicators ema,macd,rsi,atr,bbands \
    --output output/analysis.csv
```

**支持的指标**: ema, macd, adx, rsi, cci, stoch, atr, bbands, obv, ad, volume_sma, vwma, change, mid_price

**支持的周期**: 5m, 10m, 15m, 30m, 60m, 120m, 1h, 4h, day, week, month

**详细用法与量化规则示例**: [K线数据获取指南](candlesticks_guide.md)

---

### talib_calculator.py - 内部指标计算库

**位置**: `stock-analysis/scripts/talib_calculator.py`

**功能**: 技术指标计算库（内部使用，不需要直接调用）。

由 `longport_candlesticks.py` 在后台使用，通过 `--indicators` 参数指定要计算的指标即可。

---

## 环境配置

### 依赖管理
- 各脚本通过 PEP 723 元数据声明依赖
- 使用 `uv run` 自动解析和加载依赖

### API 认证
`.env` 文件需配置以下变量：
```
LONGPORT_APP_KEY=your_app_key
LONGPORT_APP_SECRET=your_app_secret
LONGPORT_ACCESS_TOKEN=your_access_token
```

### 数据格式
- **编码**: UTF-8
- **日期格式**: ISO 8601 (YYYY-MM-DD HH:MM:SS)
- **数值精度**: 股价 2-4 位小数，成交量整数，指标 2-4 位小数

详见: [CSV 导出规范](../assets/csv_template.md)
