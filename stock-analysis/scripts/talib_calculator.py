"""技术指标计算工具,基于 TA-Lib 提供多类型行情指标计算。

指标分类:
1. 基础指标: ROCR(涨幅), MIDPRICE(中间价)
2. 趋势方向: EMA(指数移动平均), MACD(趋势转换)
3. 趋势强度: ADX(趋势力度评估)
4. 动量指标: CCI(极端偏离), RSI(超买超卖), STOCH(区间扫点)
5. 波动指标: ATR(波动幅度), BBANDS(震荡区间)
6. 成交量: OBV(资金流向), AD(吸筹与派发)

Main Functions:
  - compute_change: 多周期涨幅 (ROCR)
  - compute_ema: 指数移动平均 (EMA)
  - compute_macd: 趋势转换 (MACD)
  - compute_adx: 趋势力度 (ADX)
  - compute_rsi: 超买超卖 (RSI)
  - compute_cci: 极端偏离 (CCI)
  - compute_stoch: 随机指标 (KDJ)
  - compute_atr: 波动幅度 (ATR)
  - compute_bbands: 布林带 (Bollinger Bands)
  - compute_obv: 资金流向 (OBV)
  - compute_ad: 吸筹派发 (A/D)
  - compute_volume_sma: 成交量移动平均
  - compute_vwma: 成交量加权均线

Usage:
  df = pd.read_csv('candlesticks.csv')
  df = compute_ema(df)
  df = compute_macd(df)
"""

from collections.abc import Sequence
from typing import cast

import numpy as np
import pandas as pd
import talib

# ============================================================================
# 默认参数配置
# ============================================================================
# 列名: close, high, low, volume
# 涨幅周期: 1, 5, 10, 20
# EMA 周期: 5, 10, 20, 60
# MACD 周期: (12, 26, 9)
# ADX 周期: 14, 7
# RSI 周期: 7, 14
# CCI 周期: 14, 7
# STOCH 周期: (9, 3, 3)
# ATR 周期: 3, 14
# Bollinger Bands: (5, 2.0, 2.0, SMA)
# 成交量 SMA 周期: 5, 10, 20
# VWMA 周期: 5, 10
# ============================================================================


# ==================== 内部辅助函数 ====================


def _column_as_ndarray(frame: pd.DataFrame, column: str) -> np.ndarray:
    """将 DataFrame 列转换为 numpy 数组."""
    return frame[column].to_numpy(dtype=float, copy=False)


def _ensure_columns(frame: pd.DataFrame, columns: Sequence[str]) -> None:
    """验证 DataFrame 包含所需列."""
    missing = [col for col in columns if col not in frame.columns]
    if missing:
        raise ValueError(f"DataFrame 缺少必需列: {', '.join(missing)}")


def _get_columns_data(
    frame: pd.DataFrame,
    column_names: Sequence[str],
) -> list[np.ndarray]:
    """获取多个列的数据并验证其存在."""
    _ensure_columns(frame, column_names)
    return [_column_as_ndarray(frame, col) for col in column_names]

    # ==================== 基础指标 ====================


def compute_change(
    frame: pd.DataFrame,
    *,
    change_periods: Sequence[int] | None = None,
    close_column: str = "close",
) -> pd.DataFrame:
    """计算多周期涨幅 (ROCR)

    衡量价格波动速度,突破 1.0 动量增强,低于 1.0 减弱。

    Args:
        frame: 输入 DataFrame
        change_periods: 周期列表,默认 (1, 5, 10, 20)
        close_column: 收盘价列名

    Returns:
        附加涨幅列的 DataFrame
    """
    periods = tuple(change_periods or (1, 5, 10, 20))
    _ensure_columns(frame, [close_column])
    result = frame.copy()
    close = _column_as_ndarray(result, close_column)
    for period in periods:
        result[f"change_pct_{period}"] = np.round(talib.ROCP(close, timeperiod=period), 5)
    return result


def compute_mid_price(
    frame: pd.DataFrame,
    *,
    high_column: str = "high",
    low_column: str = "low",
) -> pd.DataFrame:
    """计算高低价均值,生成中间价列."""
    _ensure_columns(frame, [high_column, low_column])
    result = frame.copy()
    high = _column_as_ndarray(result, high_column)
    low = _column_as_ndarray(result, low_column)
    result["mid_price"] = np.round(talib.MIDPRICE(high, low, timeperiod=2), 3)
    return result


# ==================== 趋势方向 ====================


def compute_ema(
    frame: pd.DataFrame,
    *,
    ema_periods: Sequence[int] | None = None,
    close_column: str = "close",
) -> pd.DataFrame:
    """使用 TA-Lib 计算多周期 EMA, 返回附加指标列后的 DataFrame.

    Args:
        frame: 输入 DataFrame
        ema_periods: 周期列表,默认 (5, 10, 20, 60)
        close_column: 收盘价列名

    Returns:
        附加 EMA 列的 DataFrame
    """
    periods = tuple(ema_periods or (5, 10, 20, 60))
    _ensure_columns(frame, [close_column])
    result = frame.copy()
    close = _column_as_ndarray(result, close_column)
    for period in periods:
        column_name = f"ema_{period}"
        result[column_name] = np.round(talib.EMA(close, timeperiod=period), 3)
    return result


def compute_macd(
    frame: pd.DataFrame,
    *,
    macd_periods: Sequence[int] | None = None,
    close_column: str = "close",
) -> pd.DataFrame:
    """计算 MACD 及其 signal/histogram.

    Args:
        frame: 输入 DataFrame
        macd_periods: (fast, slow, signal) 周期,默认 (12, 26, 9)
        close_column: 收盘价列名

    Returns:
        附加 MACD 列的 DataFrame
    """
    periods = tuple(macd_periods or (12, 26, 9))
    if len(periods) != 3:
        raise ValueError("MACD 参数必须是 (fast, slow, signal) 三个整数")
    _ensure_columns(frame, [close_column])
    result = frame.copy()
    close = _column_as_ndarray(result, close_column)
    fast, slow, signal = periods
    macd, macd_signal, macd_hist = talib.MACD(
        close, fastperiod=fast, slowperiod=slow, signalperiod=signal
    )
    result["macd"] = np.round(macd, 3)
    result["macd_signal"] = np.round(macd_signal, 3)
    result["macd_hist"] = np.round(macd_hist, 3)
    return result


# ==================== 趋势强度 ====================


def compute_adx(
    frame: pd.DataFrame,
    *,
    adx_periods: Sequence[int] | None = None,
    high_column: str = "high",
    low_column: str = "low",
    close_column: str = "close",
) -> pd.DataFrame:
    """计算多周期 ADX 指标.

    Args:
        frame: 输入 DataFrame
        adx_periods: 周期列表,默认 (14, 7)
        high_column: 最高价列名
        low_column: 最低价列名
        close_column: 收盘价列名

    Returns:
        附加 ADX 列的 DataFrame
    """
    periods = tuple(adx_periods or (14, 7))
    _ensure_columns(frame, [high_column, low_column, close_column])
    result = frame.copy()
    high = _column_as_ndarray(result, high_column)
    low = _column_as_ndarray(result, low_column)
    close = _column_as_ndarray(result, close_column)
    for period in periods:
        result[f"adx_{period}"] = np.round(talib.ADX(high, low, close, timeperiod=period), 3)
    return result


# ==================== 动量指标 ====================


def compute_rsi(
    frame: pd.DataFrame,
    *,
    rsi_periods: Sequence[int] | None = None,
    close_column: str = "close",
) -> pd.DataFrame:
    """计算多周期 RSI 指标.

    Args:
        frame: 输入 DataFrame
        rsi_periods: 周期列表,默认 (7, 14)
        close_column: 收盘价列名

    Returns:
        附加 RSI 列的 DataFrame
    """
    periods = tuple(rsi_periods or (7, 14))
    _ensure_columns(frame, [close_column])
    result = frame.copy()
    close = _column_as_ndarray(result, close_column)
    for period in periods:
        result[f"rsi_{period}"] = np.round(talib.RSI(close, timeperiod=period), 3)
    return result


def compute_cci(
    frame: pd.DataFrame,
    *,
    cci_periods: Sequence[int] | None = None,
    high_column: str = "high",
    low_column: str = "low",
    close_column: str = "close",
) -> pd.DataFrame:
    """计算多周期 CCI 指标.

    Args:
        frame: 输入 DataFrame
        cci_periods: 周期列表,默认 (14, 7)
        high_column: 最高价列名
        low_column: 最低价列名
        close_column: 收盘价列名

    Returns:
        附加 CCI 列的 DataFrame
    """
    periods = tuple(cci_periods or (14, 7))
    _ensure_columns(frame, [high_column, low_column, close_column])
    result = frame.copy()
    high = _column_as_ndarray(result, high_column)
    low = _column_as_ndarray(result, low_column)
    close = _column_as_ndarray(result, close_column)
    for period in periods:
        result[f"cci_{period}"] = np.round(talib.CCI(high, low, close, timeperiod=period), 3)
    return result


def compute_stoch(
    frame: pd.DataFrame,
    *,
    stoch_periods: Sequence[int] | None = None,
    high_column: str = "high",
    low_column: str = "low",
    close_column: str = "close",
) -> pd.DataFrame:
    """计算 Stochastic Oscillator (KDJ) 指标.

    Args:
        frame: 输入 DataFrame
        stoch_periods: (period, fastk_period, fastd_period),默认 (9, 3, 3)
        high_column: 最高价列名
        low_column: 最低价列名
        close_column: 收盘价列名

    Returns:
        附加 Stoch K/D 列的 DataFrame
    """
    periods = tuple(stoch_periods or (9, 3, 3))
    if len(periods) != 3:
        raise ValueError("STOCH 参数必须是 (period, fastk_period, fastd_period) 三个整数")
    _ensure_columns(frame, [high_column, low_column, close_column])
    result = frame.copy()
    high = _column_as_ndarray(result, high_column)
    low = _column_as_ndarray(result, low_column)
    close = _column_as_ndarray(result, close_column)
    period, fastk_period, fastd_period = periods
    k_line, d_line = talib.STOCH(
        high,
        low,
        close,
        fastk_period=period,
        slowk_period=fastk_period,
        slowd_period=fastd_period,
    )
    result[f"stoch_k_{period}"] = np.round(k_line, 3)
    result[f"stoch_d_{period}"] = np.round(d_line, 3)
    return result


# ==================== 波动指标 ====================


def compute_atr(
    frame: pd.DataFrame,
    *,
    atr_periods: Sequence[int] | None = None,
    high_column: str = "high",
    low_column: str = "low",
    close_column: str = "close",
) -> pd.DataFrame:
    """计算多周期 ATR.

    Args:
        frame: 输入 DataFrame
        atr_periods: 周期列表,默认 (3, 14)
        high_column: 最高价列名
        low_column: 最低价列名
        close_column: 收盘价列名

    Returns:
        附加 ATR 列的 DataFrame
    """
    periods = tuple(atr_periods or (3, 14))
    _ensure_columns(frame, [high_column, low_column, close_column])
    result = frame.copy()
    high = _column_as_ndarray(result, high_column)
    low = _column_as_ndarray(result, low_column)
    close = _column_as_ndarray(result, close_column)
    for period in periods:
        result[f"atr_{period}"] = np.round(talib.ATR(high, low, close, timeperiod=period), 3)
    return result


def compute_bbands(
    frame: pd.DataFrame,
    *,
    bbands_params: Sequence[int | float] | None = None,
    close_column: str = "close",
) -> pd.DataFrame:
    """使用 TA-Lib 计算布林带(Bollinger Bands).

    Args:
        frame: 输入 DataFrame
        bbands_params: (timeperiod, nbdev_up, nbdev_dn, matype),默认 (5, 2.0, 2.0, SMA)
        close_column: 收盘价列名

    Returns:
        附加 BBANDS 列的 DataFrame
    """
    _ensure_columns(frame, [close_column])
    result = frame.copy()
    close = _column_as_ndarray(result, close_column)

    params = tuple(bbands_params or (5, 2.0, 2.0, talib.MA_Type.SMA))
    if len(params) != 4:
        raise ValueError("BBANDS 参数必须是 (timeperiod, nbdev_up, nbdev_dn, matype) 四个值")

    timeperiod_val = int(params[0])
    nbdev_up_val = float(params[1])
    nbdev_dn_val = float(params[2])
    matype_val = cast(talib.MA_Type, params[3])

    upper, middle, lower = talib.BBANDS(
        close,
        timeperiod=timeperiod_val,
        nbdevup=nbdev_up_val,
        nbdevdn=nbdev_dn_val,
        matype=matype_val,
    )

    result[f"bb_upper_{timeperiod_val}"] = np.round(upper, 3)
    result[f"bb_middle_{timeperiod_val}"] = np.round(middle, 3)
    result[f"bb_lower_{timeperiod_val}"] = np.round(lower, 3)

    return result


# ==================== 成交量 ====================


def compute_obv(
    frame: pd.DataFrame,
    *,
    close_column: str = "close",
    volume_column: str = "volume",
) -> pd.DataFrame:
    """计算 OBV (On-Balance Volume) 指标.

    Args:
        frame: 输入 DataFrame
        close_column: 收盘价列名
        volume_column: 成交量列名

    Returns:
        附加 OBV 列的 DataFrame
    """
    _ensure_columns(frame, [close_column, volume_column])
    result = frame.copy()
    close = _column_as_ndarray(result, close_column)
    volume = _column_as_ndarray(result, volume_column)
    result["obv"] = np.round(talib.OBV(close, volume), 3)
    return result


def compute_ad(
    frame: pd.DataFrame,
    *,
    high_column: str = "high",
    low_column: str = "low",
    close_column: str = "close",
    volume_column: str = "volume",
) -> pd.DataFrame:
    """计算 AD (Accumulation/Distribution) 指标.

    Args:
        frame: 输入 DataFrame
        high_column: 最高价列名
        low_column: 最低价列名
        close_column: 收盘价列名
        volume_column: 成交量列名

    Returns:
        附加 AD 列的 DataFrame
    """
    _ensure_columns(frame, [high_column, low_column, close_column, volume_column])
    result = frame.copy()
    high = _column_as_ndarray(result, high_column)
    low = _column_as_ndarray(result, low_column)
    close = _column_as_ndarray(result, close_column)
    volume = _column_as_ndarray(result, volume_column)
    result["ad"] = np.round(talib.AD(high, low, close, volume), 3)
    return result


def compute_volume_sma(
    frame: pd.DataFrame,
    *,
    volume_sma_periods: Sequence[int] | None = None,
    volume_column: str = "volume",
) -> pd.DataFrame:
    """计算成交量的多周期 SMA(简单移动平均).

    Args:
        frame: 输入 DataFrame
        volume_sma_periods: 周期列表,默认 (5, 10, 20)
        volume_column: 成交量列名

    Returns:
        附加成交量 SMA 列的 DataFrame
    """
    periods = tuple(volume_sma_periods or (5, 10, 20))
    _ensure_columns(frame, [volume_column])
    result = frame.copy()
    volume = _column_as_ndarray(result, volume_column)
    for period in periods:
        result[f"volume_sma_{period}"] = np.round(talib.SMA(volume, timeperiod=period), 3)
    return result


def compute_vwma(
    frame: pd.DataFrame,
    *,
    vwma_periods: Sequence[int] | None = None,
    close_column: str = "close",
    volume_column: str = "volume",
) -> pd.DataFrame:
    """计算成交量加权移动平均线 (VWMA).

    VWMA 通过成交量加权价格,成交量大的交易日对均线影响更大。
    计算公式: VWMA = SUM(价格 * 成交量) / SUM(成交量)

    Args:
        frame: 输入 DataFrame
        vwma_periods: 周期列表,默认 (5, 10)
        close_column: 收盘价列名
        volume_column: 成交量列名

    Returns:
        附加 VWMA 列的 DataFrame
    """
    periods = tuple(vwma_periods or (5, 10))
    _ensure_columns(frame, [close_column, volume_column])
    result = frame.copy()
    close = _column_as_ndarray(result, close_column)
    volume = _column_as_ndarray(result, volume_column)

    for period in periods:
        # 计算价格*成交量的移动总和
        pv_sum = talib.SUM(close * volume, timeperiod=period)
        # 计算成交量的移动总和
        v_sum = talib.SUM(volume, timeperiod=period)
        # VWMA = (价格*成交量)之和 / 成交量之和
        result[f"vwma_{period}"] = np.round(pv_sum / v_sum, 3)

    return result


__all__ = [
    "compute_ad",
    "compute_adx",
    "compute_atr",
    "compute_bbands",
    "compute_cci",
    "compute_change",
    "compute_ema",
    "compute_macd",
    "compute_mid_price",
    "compute_obv",
    "compute_rsi",
    "compute_stoch",
    "compute_volume_sma",
    "compute_vwma",
]
