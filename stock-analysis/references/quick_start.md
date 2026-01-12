# 快速开始指南

本指南通过端到端示例展示如何使用 stock-analysis 完成股票分析工作流。

## 前置条件

1. **LongPort 账户**: 需要有效的 LongPort 账户和 API 凭证
2. **环境配置**: `.env` 文件配置以下变量
   ```
   LONGPORT_APP_KEY=your_app_key
   LONGPORT_APP_SECRET=your_app_secret
   LONGPORT_ACCESS_TOKEN=your_access_token
   ```
3. **依赖**: `uv` 包管理器（自动处理脚本依赖）

## 工作流示例

### 场景 1: 获取特定股票的日线数据与技术指标

**目标**: 获取腾讯控股 (700.HK) 最近 100 个交易日的日线数据，计算完整技术指标。

```bash
# 1. 获取日线数据及所有推荐指标
uv run stock-analysis/scripts/longport_candlesticks.py \
    --symbol 700.HK \
    --period day \
    --count 100 \
    --indicators ema,macd,rsi,atr,bbands,obv \
    --output output/700_hk_day.csv

# 2. 检查输出文件
head -5 output/700_hk_day.csv
```

**输出 CSV 示例**:
```
symbol,datetime,open,high,low,close,volume,turnover,ema_5,ema_10,ema_20,ema_60,macd,macd_signal,macd_hist,rsi_7,rsi_14,...
700.HK,2024-01-15 00:00:00,350.50,352.30,349.80,351.20,50000000,17556000000,350.85,350.42,349.95,348.50,1.23,0.98,0.25,65.2,58.3,...
700.HK,2024-01-16 00:00:00,351.20,353.10,350.90,352.80,52000000,18456000000,351.53,350.97,350.38,348.92,1.45,1.15,0.30,68.5,61.2,...
```

**分析要点**:
- `ema_5 > ema_10 > ema_20`: 短期强势上升信号
- `macd > 0` 且 `macd_hist > 0`: 中期看涨
- `rsi_14 > 70`: 可能超买，考虑获利回吐
- 使用 `bb_upper` 和 `bb_lower` 判断当前价格处于震荡带的位置

---

### 场景 2: 批量获取自选清单中的股票数据

**目标**: 获取"科技股"自选清单中所有股票的 4 小时线数据。

```bash
# 1. 列出所有自选清单
uv run stock-analysis/scripts/longport_groups.py list

# 输出示例:
# ┌─────────────┬────────────┬──────────────┐
# │ Group ID    │ Group Name │ Member Count │
# ├─────────────┼────────────┼──────────────┤
# │ 4038104     │ 科技股     │ 5            │
# │ 4038105     │ 金融股     │ 3            │
# └─────────────┴────────────┴──────────────┘

# 2. 获取"科技股"清单的成员符号
uv run stock-analysis/scripts/longport_groups.py get-symbols \
    --id 4038104 \
    --output output/tech_stocks.txt

# 3. 查看清单成员
cat output/tech_stocks.txt
# 输出:
# 700.HK
# 9988.HK
# AAPL.US
# MSFT.US
# NVDA.US

# 4. 为每只股票获取 4 小时线数据与指标
for symbol in $(cat output/tech_stocks.txt); do
    uv run stock-analysis/scripts/longport_candlesticks.py \
        --symbol "$symbol" \
        --period 4h \
        --count 100 \
        --output "output/${symbol}_4h.csv" \
        --indicators ema,macd,rsi,atr
done

# 5. 合并所有输出（可选，使用 Python/pandas）
python3 << 'EOF'
import pandas as pd
import glob

# 读取所有 CSV 文件
dfs = [pd.read_csv(f) for f in glob.glob("output/*_4h.csv")]
combined = pd.concat(dfs, ignore_index=True)

# 按 symbol 和 datetime 排序
combined = combined.sort_values(['symbol', 'datetime'])

# 保存合并结果
combined.to_csv('output/all_tech_stocks_4h.csv', index=False)
print(f"✓ 合并 {len(dfs)} 只股票的数据，共 {len(combined)} 行")
EOF
```

---

### 场景 3: 创建新的自选清单并管理成员

**目标**: 创建"美股龙头"清单，管理其中的股票符号。

```bash
# 1. 创建新分组，可选初始化符号
uv run stock-analysis/scripts/longport_groups.py create \
    --name "美股龙头" \
    --symbols AAPL.US,MSFT.US,GOOGL.US

# 2. 查看新创建的分组
uv run stock-analysis/scripts/longport_groups.py list

# 3. 添加新的符号到分组（假设新创建的分组 ID 为 4038106）
uv run stock-analysis/scripts/longport_groups.py update \
    --id 4038106 \
    --add-symbols TSLA.US,META.US,NVDA.US

# 4. 移除某个符号
uv run stock-analysis/scripts/longport_groups.py update \
    --id 4038106 \
    --remove-symbols GOOGL.US

# 5. 导出更新后的成员列表
uv run stock-analysis/scripts/longport_groups.py get-symbols \
    --id 4038106 \
    --output output/us_leaders.txt
```

---

### 场景 4: 批量获取自定义指标组合

**目标**: 为多只股票获取特定指标组合（不需要所有指标）。

```bash
# 仅获取趋势指标（EMA、MACD）和动量指标（RSI）
for symbol in 700.HK 9988.HK AAPL.US; do
    uv run stock-analysis/scripts/longport_candlesticks.py \
        --symbol "$symbol" \
        --period day \
        --count 100 \
        --indicators ema,macd,rsi \
        --output "output/${symbol}_trend.csv"
done

# 检查输出
head -1 output/700.HK_trend.csv
# 输出的列: symbol, datetime, open, high, low, close, volume, turnover, ema_5, ema_10, ema_20, ema_60, macd, macd_signal, macd_hist, rsi_7, rsi_14
```

**支持的指标参数**:

逗号分隔列表，按需组合：
- 趋势：`ema`, `macd`, `adx`
- 动量：`rsi`, `cci`, `stoch`
- 波动：`atr`, `bbands`
- 成交量：`obv`, `ad`, `volume_sma`, `vwma`
- 基础：`change`, `mid_price`

---

### 场景 5: 快速获取完整分析（推荐）

**目标**: 一键获取 K 线数据 + 完整技术指标，用于综合分析。

---

## 常见问题

### Q1: 如何处理网络错误？

A: 脚本内置错误处理，失败时返回 `None` 并打印错误信息。建议重试或检查网络连接。

```bash
# 如果失败，检查错误信息
uv run stock-analysis/scripts/longport_candlesticks.py --symbol 700.HK --period day --count 100
# 输出: ✗ 获取数据失败: [错误原因]
```

### Q2: 支持哪些股票代码格式？

A: 使用 LongPort 标准格式：
- 港股: `700.HK` (香港), `000001.SZ` (深圳)
- 美股: `AAPL.US` (纳斯达克), `BRK.US` (纽约)
- A 股: `600000.SH` (上海), `000858.SZ` (深圳)

### Q3: CSV 输出的列太多了，如何只获取需要的指标？

A: 通过 `--indicators` 参数选择性指定，只计算需要的指标。参考场景 4 的例子。

### Q4: 指标计算结果中有 NaN 值？

A: 这是正常的，指标计算需要历史数据窗口。前几行会有 NaN。可以在后续处理中删除或填充。

### Q5: 如何加快大批量数据获取？

A: 
1. **缓存**: 避免重复获取同一数据，保存为 CSV
2. **指标选择**: 仅指定需要的指标，减少计算量（参考场景 4）
3. **并发**: 使用 bash 循环或 Python 并发库并行处理多个符号

---

## 最佳实践

1. **指标选择**: 根据分析需求选择指标组合（参考 [指标参考](indicator_reference.md)）
2. **周期选择**: 针对不同交易时间选择合适的 K 线周期
3. **参数一致性**: 同一分析中保持复权方式一致（推荐前复权）
4. **背景验证**: 关键交易信号前通过多个指标交叉确认
5. **定期更新**: 设定定期更新时间（如每天收盘后），避免频繁调用 API

---

## 参考资源
````

- [工作流文档](api_workflow.md) - 详细的 API 说明和数据格式规范
- [指标参考](indicator_reference.md) - 40+ 技术指标的计算原理和应用
- LongPort API 文档: https://open.longportapp.com/
