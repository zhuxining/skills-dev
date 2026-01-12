# K线数据获取与量化规则应用指南

本文档介绍如何使用 `longport_candlesticks.py` 获取最新 N 条数据，并应用技术分析规则进行量化分析。

## 核心工作流

```
导出符号列表 (groups_management.md)
        ↓
获取最新 N 条 K 线数据 (此文档)
        ↓
计算技术指标 (内部完成)
        ↓
应用量化规则 (参考 indicator_reference.md)
        ↓
生成分析结果并导出
```

## 基础概念

### K 线数据
K 线（Candlestick）是表示一个时间周期内价格变化的图表。每一条 K 线包含：
- **Open (开)**: 周期开始的价格
- **High (高)**: 周期内的最高价
- **Low (低)**: 周期内的最低价
- **Close (收)**: 周期结束时的价格
- **Volume**: 成交量
- **Turnover**: 成交额（货币单位）

### 周期
股票数据的"周期"指数据的粒度（时间跨度）：

| 周期 | 说明 | 典型用途 |
|------|------|--------|
| 5m, 10m, 15m, 30m | 分钟线 | 日内高频交易 |
| 60m, 120m, 1h, 4h | 小时线 | 日内中期交易 |
| day | 日线 | 中期趋势跟踪 |
| week | 周线 | 长期趋势分析 |
| month | 月线 | 极长期战略分析 |

---

## 使用指南

### 最简单的用法：获取最新 100 条日线数据

```bash
uv run stock-analysis/scripts/longport_candlesticks.py \
    --symbol 700.HK \
    --period day \
    --count 100
```

**输出**: 包含 OHLCV 数据的表格（直接打印到终端）

**参数说明**:
- `--symbol`: 股票代码（必需）
  - 香港: `700.HK`, `9988.HK`, `000001.SZ`
  - 美股: `AAPL.US`, `MSFT.US`, `TSLA.US`
- `--period`: K 线周期（默认 day）
  - 支持: 5m, 10m, 15m, 30m, 60m, 120m, 1h, 4h, day, week, month
- `--count`: 返回的数据条数（默认 100）
  - 范围通常在 1-1000 之间，根据 API 限制而定
- `--output`: 输出文件路径（可选，不指定则打印到终端）

---

### 获取数据并添加指标

```bash
uv run stock-analysis/scripts/longport_candlesticks.py \
    --symbol 700.HK \
    --period day \
    --count 200 \
    --indicators ema,macd,rsi,atr,bbands,obv \
    --output output/700_hk_analysis.csv
```

**输出列示例**:
```
symbol,datetime,open,high,low,close,volume,turnover,ema_5,ema_10,ema_20,ema_60,macd,macd_signal,macd_hist,rsi_7,rsi_14,atr_3,atr_14,bb_upper,bb_middle,bb_lower,bb_pct,obv
700.HK,2024-01-08,...,[OHLCV data],...,[indicator values]...
700.HK,2024-01-09,...,[OHLCV data],...,[indicator values]...
```

**支持的指标** (逗号分隔):
- 趋势: `ema`, `macd`, `adx`
- 动量: `rsi`, `cci`, `stoch`
- 波动: `atr`, `bbands`
- 成交量: `obv`, `ad`, `volume_sma`, `vwma`
- 基础: `change`, `mid_price`

详细的指标定义见 [技术指标参考](indicator_reference.md)。

---

## 量化规则应用示例

本部分展示如何从获取数据到应用量化规则的完整工作流。

### 示例 1: EMA 均线交叉策略

**规则**: 当短期 EMA(5) 上穿中期 EMA(20) 时，生成看涨信号。

**步骤**:

#### Step 1: 获取数据并计算 EMA

```bash
uv run stock-analysis/scripts/longport_candlesticks.py \
    --symbol 700.HK \
    --period day \
    --count 100 \
    --indicators ema \
    --output data.csv
```

#### Step 2: 应用规则并生成信号

```python
#!/usr/bin/env python3
import pandas as pd

# 读取数据
df = pd.read_csv('data.csv', parse_dates=['datetime'])
df = df.sort_values('datetime')

# 计算信号：EMA5 > EMA20 为看涨
df['signal'] = (df['ema_5'] > df['ema_20']).astype(int)

# 计算交叉点（从 0 变为 1 的位置）
df['crossover'] = df['signal'].diff() == 1

# 输出买入信号
buy_signals = df[df['crossover']][['datetime', 'close', 'ema_5', 'ema_20']]

print("均线交叉买入信号:")
print(buy_signals)

# 保存结果
buy_signals.to_csv('ema_crossover_signals.csv', index=False)
```

**输出示例**:
```
            datetime   close   ema_5  ema_20
2024-01-15 00:00:00  351.20  350.85  349.95  ← EMA5 上穿 EMA20，买入信号
2024-01-20 00:00:00  356.50  355.12  352.30
```

**应用**: 在这些日期，如果其他确认指标也支持（如成交量放大、RSI 未超卖），可以考虑建仓。

---

### 示例 2: RSI 超卖买入策略

**规则**: 当 RSI(14) < 30 时，股票处于超卖状态，可能反弹。

**步骤**:

#### Step 1: 获取数据

```bash
uv run stock-analysis/scripts/longport_candlesticks.py \
    --symbol AAPL.US \
    --period 4h \
    --count 100 \
    --indicators rsi,atr \
    --output aapl_rsi_data.csv
```

#### Step 2: 筛选超卖信号

```python
#!/usr/bin/env python3
import pandas as pd

df = pd.read_csv('aapl_rsi_data.csv', parse_dates=['datetime'])

# 超卖条件
oversold = df[df['rsi_14'] < 30][['datetime', 'close', 'rsi_14', 'atr_14']]

print("RSI 超卖买入机会:")
print(oversold)

# 计算风险管理的止损位置
oversold['stop_loss'] = oversold['close'] - oversold['atr_14'] * 1.5

print("\n建议止损位置（Close - ATR×1.5）:")
print(oversold[['datetime', 'close', 'rsi_14', 'stop_loss']])

oversold.to_csv('rsi_oversold_signals.csv', index=False)
```

**输出示例**:
```
            datetime   close  rsi_14  atr_14  stop_loss
2024-01-10 12:00:00  175.50  28.5    2.30    172.95    ← RSI 超卖，建议止损在 172.95
2024-01-12 16:00:00  176.20  29.8    2.25    173.83
```

**应用**: 在这些位置可以考虑建仓，设置止损位避免大幅亏损。

---

### 示例 3: MACD 趋势确认策略

**规则**: 当 MACD > 0 且 MACD_hist > 0 时，表示上升趋势强劲。结合 ADX > 20 确认趋势存在。

**步骤**:

#### Step 1: 获取完整数据

```bash
uv run stock-analysis/scripts/longport_candlesticks.py \
    --symbol 9988.HK \
    --period day \
    --count 200 \
    --indicators macd,adx,ema \
    --output alibaba_trend.csv
```

#### Step 2: 应用多层确认规则

```python
#!/usr/bin/env python3
import pandas as pd

df = pd.read_csv('alibaba_trend.csv', parse_dates=['datetime'])
df = df.sort_values('datetime')

# 规则 1: MACD 看涨
macd_bullish = (df['macd'] > 0) & (df['macd_hist'] > 0)

# 规则 2: 趋势强度足够
trend_strong = df['adx_14'] > 20

# 规则 3: 价格在均线上方
above_ema = df['close'] > df['ema_20']

# 综合条件
strong_uptrend = macd_bullish & trend_strong & above_ema

signals = df[strong_uptrend][['datetime', 'close', 'macd', 'adx_14', 'ema_20']]

print("强上升趋势信号（多层确认）:")
print(signals)

signals.to_csv('strong_uptrend_signals.csv', index=False)
```

**输出示例**:
```
            datetime   close     macd   adx_14  ema_20
2024-01-15 00:00:00  120.50  0.8500   35.2    118.90  ← MACD正 & ADX强 & 价格高于EMA20
2024-01-16 00:00:00  121.30  1.0200   36.5    119.30
2024-01-17 00:00:00  122.10  1.1500   37.2    119.80
```

**应用**: 这类高置信度信号可以用于建立趋势跟踪仓位。

---

### 示例 4: 批量股票风险评估

**目标**: 为多只股票快速评估当前风险/机会比例。

```bash
# 1. 从分组导出符号列表（见 groups_management.md）
uv run stock-analysis/scripts/longport_groups.py get-symbols \
    --id 4038104 \
    --output tech_stocks.txt

# 2. 批量获取数据并计算指标
python3 << 'EOF'
import subprocess
import pandas as pd
import glob

symbols = [s.strip() for s in open('tech_stocks.txt')]
results = []

for symbol in symbols:
    # 获取最新 50 条日线数据
    subprocess.run([
        'uv', 'run', 'stock-analysis/scripts/longport_candlesticks.py',
        '--symbol', symbol,
        '--period', 'day',
        '--count', '50',
        '--indicators', 'rsi,bbands,atr',
        '--output', f'temp_{symbol}.csv'
    ])
    
    df = pd.read_csv(f'temp_{symbol}.csv')
    
    # 取最新一行
    latest = df.iloc[-1]
    
    # 评估
    rsi_signal = 'Oversold' if latest['rsi_14'] < 30 else 'Normal' if latest['rsi_14'] < 70 else 'Overbought'
    bb_position = (latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower'])
    
    results.append({
        'symbol': symbol,
        'price': latest['close'],
        'rsi_14': latest['rsi_14'],
        'signal': rsi_signal,
        'bb_pct': bb_position,
        'atr_14': latest['atr_14']
    })

# 汇总输出
summary = pd.DataFrame(results)
summary = summary.sort_values('bb_pct')  # 按 BB 位置排序（机会）

print("科技股池机会评估:")
print(summary)

summary.to_csv('opportunity_assessment.csv', index=False)
EOF
```

**输出示例**:
```
  symbol   price rsi_14     signal  bb_pct atr_14
700.HK    351.2   28.5  Oversold     0.15   2.30  ← 低位机会
MSFT.US   420.5   65.3  Normal       0.55   3.20
AAPL.US   195.8   72.1  Overbought   0.85   2.80
```

---

## 工作流集成示例

### 完整的日常分析流程

```bash
#!/bin/bash
# daily_analysis.sh

PORTFOLIO_ID=4038104
OUTPUT_DIR="daily_reports/$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"

# 1. 导出投资组合
uv run stock-analysis/scripts/longport_groups.py get-symbols \
    --id $PORTFOLIO_ID \
    --output "$OUTPUT_DIR/symbols.txt"

# 2. 为每只股票获取最新数据
for symbol in $(cat "$OUTPUT_DIR/symbols.txt"); do
    echo "Fetching data for $symbol..."
    uv run stock-analysis/scripts/longport_candlesticks.py \
        --symbol "$symbol" \
        --period day \
        --count 100 \
        --indicators ema,macd,rsi,atr,bbands \
        --output "$OUTPUT_DIR/${symbol}.csv"
done

# 3. 运行分析脚本
python3 daily_analysis_script.py "$OUTPUT_DIR"

# 4. 生成报告
echo "Daily analysis report generated in $OUTPUT_DIR"
```

---

## 常见问题

### Q: 获取数据时显示"API limit exceeded"

**A**: LongPort API 有频率限制。解决方案：
- 使用缓存：定期获取一次数据并保存为 CSV，后续使用本地文件
- 分散请求：在不同时间获取不同股票的数据
- 减少 count 参数，只获取必要的行数

### Q: 如何快速获取仅最新一条数据？

**A**: 使用 `--count 1`
```bash
uv run stock-analysis/scripts/longport_candlesticks.py \
    --symbol 700.HK \
    --period day \
    --count 1 \
    --indicators rsi,bbands
```

### Q: CSV 文件很大，如何处理？

**A**: 
1. 减少 `--count` 参数值
2. 仅指定必需的指标：`--indicators ema,rsi` （而不是所有指标）
3. 使用 pandas 读取后筛选列：`df[['datetime', 'close', 'ema_20', 'rsi_14']]`

### Q: 指标计算出现 NaN 值？

**A**: 这是正常的，前几行会有 NaN 是因为指标计算需要历史窗口。使用时直接忽略或删除：
```python
df = df.dropna()
```

---

## 最佳实践

1. **定期更新**: 设置定时任务（如每天收盘后）自动获取最新数据
2. **多维确认**: 不要依赖单一指标，使用多个指标交叉确认（见示例 3）
3. **风险管理**: 根据 ATR 设置合理的止损位置（见示例 2）
4. **本地缓存**: 将获取的数据保存为 CSV，避免频繁调用 API
5. **规则参数化**: 将策略规则（如 RSI < 30）写成可配置的参数，便于调整和回测

---

## 下一步

- **深入指标**: 了解每个指标的详细定义和应用场景，见 [技术指标参考](indicator_reference.md)
- **自选管理**: 如何创建和维护投资组合分组，见 [自选清单管理指南](groups_management.md)
- **回测验证**: 对策略规则进行历史数据回测，验证有效性
