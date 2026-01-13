#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "longport>=3.0.18",
#     "pandas>=2.3.3",
#     "ta-lib>=0.6.8",
# ]
# ///

"""LongPort K 线数据获取工具,支持多周期行情查询与技术指标计算。

集成 LongPort API 获取K线数据与 TA-Lib 指标计算功能,支持导出包含完整指标的 CSV。

Main Functions:
  - fetch_candlesticks_with_indicators: 获取 K 线数据并计算完整技术指标
  - fetch_candlesticks: 获取标的 K 线数据并返回 pandas.DataFrame(前复权)
  - _parse_period: 解析 K 线周期字符串
  - _candlesticks_to_df: 将响应转换为 DataFrame

Usage:
  uv run longport_candlesticks.py --symbol 700.HK --period day --count 200 --output 700.hk_day.csv
  uv run longport_candlesticks.py --symbol 700.HK --period day --count 100 --indicators ema,macd,rsi

Note:
  - 所有输出统一保存在项目根目录的 output/ 文件夹
  - 可以指定子路径, 如 --output stocks/700.hk.csv
"""

import argparse
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
import sys

from longport.openapi import AdjustType, Config, Period, QuoteContext
import pandas as pd

from _output_helper import resolve_output_path
from _talib_calculator import (
    compute_ad,
    compute_adx,
    compute_atr,
    compute_bbands,
    compute_cci,
    compute_change,
    compute_ema,
    compute_macd,
    compute_mid_price,
    compute_obv,
    compute_rsi,
    compute_stoch,
    compute_volume_sma,
    compute_vwma,
)


@contextmanager
def open_quote_ctx() -> Iterator[QuoteContext]:
    """从 .env 初始化 QuoteContext,并在结束时尝试关闭。"""

    ctx = QuoteContext(Config.from_env())
    try:
        yield ctx
    finally:
        close_fn = getattr(ctx, "close", None)
        if callable(close_fn):
            close_fn()


def fetch_candlesticks(
    symbol: str,
    period: type[Period] = Period.Day,
    count: int = 100,
    adjust_type: type[AdjustType] = AdjustType.ForwardAdjust,
) -> pd.DataFrame:
    """获取标的 K 线并返回 DataFrame(index 为 UTC datetime)."""

    try:
        with open_quote_ctx() as ctx:
            resp = ctx.candlesticks(symbol, period, count, adjust_type)
    except Exception as e:
        print(f"✗ API 调用失败: {e}", file=sys.stderr)
        return pd.DataFrame()

    return _candlesticks_to_df(resp, symbol)


def fetch_candlesticks_with_indicators(
    symbol: str,
    period: type[Period] = Period.Day,
    count: int = 100,
    adjust_type: type[AdjustType] = AdjustType.ForwardAdjust,
    indicators: list[str] | None = None,
) -> pd.DataFrame:
    """获取 K 线数据并计算指定的技术指标。

    Args:
        symbol: 标的代码
        period: K线周期
        count: 获取条数
        adjust_type: 复权类型
        indicators: 指标列表。如果为 None 则计算完整套件(ema, macd, rsi, atr, obv, bbands)。
                   支持: ema, macd, rsi, adx, cci, stoch, atr, bbands, obv, ad, change, mid_price, volume_sma, vwma

    Returns:
        包含原始价格数据和指标的 DataFrame
    """
    df = fetch_candlesticks(symbol, period, count, adjust_type)

    if df.empty:
        return df

    # 如果未指定指标,计算完整套件(包含所有常用指标)
    if indicators is None:
        df = compute_change(df)  # 涨幅
        df = compute_mid_price(df)  # 中间价
        df = compute_ema(df)  # EMA
        df = compute_macd(df)  # MACD
        df = compute_rsi(df)  # RSI
        df = compute_adx(df)  # ADX
        df = compute_cci(df)  # CCI
        df = compute_stoch(df)  # KDJ
        df = compute_atr(df)  # ATR
        df = compute_bbands(df)  # 布林带
        df = compute_obv(df)  # OBV
        df = compute_ad(df)  # A/D
        df = compute_volume_sma(df)  # 成交量均线
        df = compute_vwma(df)  # 成交量加权均线
        return df

    # 计算指定的指标
    for indicator in indicators:
        if indicator == "ema":
            df = compute_ema(df)
        elif indicator == "macd":
            df = compute_macd(df)
        elif indicator == "rsi":
            df = compute_rsi(df)
        elif indicator == "adx":
            df = compute_adx(df)
        elif indicator == "cci":
            df = compute_cci(df)
        elif indicator == "stoch":
            df = compute_stoch(df)
        elif indicator == "atr":
            df = compute_atr(df)
        elif indicator == "bbands":
            df = compute_bbands(df)
        elif indicator == "obv":
            df = compute_obv(df)
        elif indicator == "ad":
            df = compute_ad(df)
        elif indicator == "change":
            df = compute_change(df)
        elif indicator == "mid_price":
            df = compute_mid_price(df)
        elif indicator == "volume_sma":
            df = compute_volume_sma(df)
        elif indicator == "vwma":
            df = compute_vwma(df)

    return df


def _candlesticks_to_df(resp, symbol: str = "") -> pd.DataFrame:
    """将 API 响应转换为 DataFrame."""
    c_list = resp if isinstance(resp, list) else getattr(resp, "candlesticks", None) or []

    if not c_list:
        return pd.DataFrame()

    records = []
    try:
        for c in c_list:
            # timestamp 已经是 datetime 对象, 无需转换
            dt = (
                c.timestamp
                if isinstance(c.timestamp, datetime)
                else datetime.fromtimestamp(c.timestamp, tz=UTC)
            )
            records.append({
                "symbol": symbol,
                "datetime": dt,
                "open": float(c.open),
                "high": float(c.high),
                "low": float(c.low),
                "close": float(c.close),
                "volume": int(c.volume),
                "turnover": float(c.turnover),
            })
    except Exception as e:
        print(f"✗ 数据转换错误: {e}", file=sys.stderr)
        return pd.DataFrame()

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.set_index("datetime").sort_index()
    return df


def _parse_period(value: str) -> type[Period]:
    mapping = {
        "5m": Period.Min_5,
        "10m": Period.Min_10,
        "15m": Period.Min_15,
        "30m": Period.Min_30,
        "60m": Period.Min_60,
        "120m": Period.Min_120,
        "1h": Period.Min_60,
        "4h": Period.Min_240,
        "day": Period.Day,
        "week": Period.Week,
        "month": Period.Month,
    }
    try:
        return mapping[value.lower()]
    except KeyError as exc:
        msg = f"不支持的 period: {value}"
        raise argparse.ArgumentTypeError(msg) from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="获取 LongPort K 线数据与技术指标,输出 CSV 或 stdout"
    )
    parser.add_argument("--symbol", required=True, help="标的代码,如 700.HK / AAPL.US")
    parser.add_argument(
        "--period",
        default="day",
        type=_parse_period,
        help="K线周期,支持: 5m,10m,15m,30m,60m,120m,1h,4h,day,week,month。默认 day",
    )
    parser.add_argument("--count", type=int, default=100, help="返回条数,默认 100")

    parser.add_argument(
        "--output",
        help="输出文件名或相对路径 (如 data.csv 或 stocks/700.hk.csv), 统一保存在 output/ 文件夹。不填则打印到 stdout。",
    )

    parser.add_argument(
        "--indicators",
        help="指标列表,逗号分隔。支持: ema,macd,rsi,adx,cci,stoch,atr,bbands,obv,ad,change,mid_price,volume_sma,vwma。"
        "不填则计算完整套件(ema+macd+rsi+atr+obv+bbands)",
    )

    args = parser.parse_args()

    # 解析指标参数
    indicators = None
    if args.indicators:
        indicators = [ind.strip() for ind in args.indicators.split(",")]

    df = fetch_candlesticks_with_indicators(
        args.symbol,
        period=args.period,
        count=args.count,
        indicators=indicators,
    )

    if df.empty:
        import sys

        print("✗ 无法获取数据. 请检查:", file=sys.stderr)
        print(
            f"  1. symbol 格式: {args.symbol} (正确格式如 700.HK, 159735.SZ, AAPL.US)",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.output:
        output_path = resolve_output_path(args.output)
        df.to_csv(output_path)
        print(f"✓ 已写入: {output_path}")
        print(f"  行数: {len(df)}")
        print(f"  列数: {len(df.columns)}")
        print(f"  时间范围: {df.index[0]} 至 {df.index[-1]}")
    else:
        print("\n=== 后 5 行数据 ===")
        print(df.tail())
        print("\n=== 汇总 ===")
        print(f"总行数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        print(f"列名: {', '.join(df.columns.tolist())}")
        print(f"时间范围: {df.index[0]} 至 {df.index[-1]}")


if __name__ == "__main__":
    main()
