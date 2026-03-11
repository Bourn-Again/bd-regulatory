"""
SEC Rule 15c3-1 Appendix A haircut schedule.
Returns (haircut_pct, haircut_dollar_amount) per position.
"""
from __future__ import annotations

from datetime import date
from typing import Optional, Tuple

import config
from models.enums import SecurityType


def _treasury_haircut(years_to_maturity: float) -> float:
    if years_to_maturity < 0.25:    return 0.000
    elif years_to_maturity < 2.0:   return 0.010
    elif years_to_maturity < 3.0:   return 0.015
    elif years_to_maturity < 5.0:   return 0.030
    elif years_to_maturity < 10.0:  return 0.040
    elif years_to_maturity < 25.0:  return 0.050
    else:                            return 0.060


def _agency_haircut(years_to_maturity: float) -> float:
    return _treasury_haircut(years_to_maturity) + 0.005


def _municipal_haircut(years_to_maturity: float) -> float:
    return 0.00 if years_to_maturity < 1.0 else 0.07


def _corp_ig_haircut(years_to_maturity: float) -> float:
    for (threshold, rate) in config.CORP_IG_HAIRCUT_SCHEDULE:
        if years_to_maturity <= threshold:
            return rate
    return 0.09


def _otc_equity_haircut(price: float) -> float:
    for (threshold, rate) in config.OTC_HAIRCUT_SCHEDULE:
        if price < threshold:
            return rate
    return 0.15


def compute_haircut(
    security_type: SecurityType,
    market_value: float,
    years_to_maturity: Optional[float] = None,
    price: Optional[float] = None,
) -> Tuple[float, float]:
    """
    Returns (haircut_pct, haircut_dollar_amount).
    market_value should be the absolute (unsigned) market value.
    """
    ytm = years_to_maturity or 0.0
    px = price or 0.0
    mv = abs(market_value)

    pct: float
    if security_type == SecurityType.US_TREASURY:
        pct = _treasury_haircut(ytm)

    elif security_type == SecurityType.AGENCY:
        pct = _agency_haircut(ytm)

    elif security_type == SecurityType.MUNICIPAL:
        pct = _municipal_haircut(ytm)

    elif security_type == SecurityType.CORP_IG:
        pct = _corp_ig_haircut(ytm)

    elif security_type == SecurityType.CORP_HY:
        pct = 0.15

    elif security_type == SecurityType.EQUITY_LISTED:
        pct = 0.15

    elif security_type == SecurityType.EQUITY_OTC:
        pct = _otc_equity_haircut(px)

    elif security_type == SecurityType.ETF:
        pct = 0.15   # treated as listed equity

    elif security_type == SecurityType.MBS:
        pct = config.MBS_HAIRCUT

    elif security_type == SecurityType.CMO:
        pct = config.CMO_HAIRCUT

    elif security_type == SecurityType.OPTION:
        pct = 1.00   # 100% of market value

    elif security_type in (SecurityType.NON_MARKETABLE, SecurityType.REPO_COLLATERAL):
        pct = 1.00

    else:
        pct = 1.00

    return pct, round(mv * pct, 2)
