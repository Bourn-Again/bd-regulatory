from __future__ import annotations
from dataclasses import dataclass
from datetime import date


@dataclass
class FailPosition:
    fail_id: str
    account_id: str
    cusip: str
    direction: str        # "FTR" (fail to receive) or "FTD" (fail to deliver)
    trade_date: date
    settle_date: date
    quantity: float
    market_value: float
    contra_party: str
    reason: str           # e.g. "LATE_DELIVERY", "WRONG_CERT", "LOCATE_FAILURE"
    business_line: str

    @property
    def days_outstanding(self) -> int:
        from config import CALCULATION_DATE
        return max((CALCULATION_DATE - self.settle_date).days, 0)

    @property
    def aging_bucket(self) -> str:
        d = self.days_outstanding
        if d <= 1:   return "T+1"
        if d <= 2:   return "T+2"
        if d <= 3:   return "T+3"
        if d <= 13:  return "T+4–13"
        return "T+13+"

    @property
    def close_out_required(self) -> bool:
        """Reg SHO Rule 204: close-out obligation triggers at T+3 for equities/ETFs."""
        return self.days_outstanding >= 3

    @property
    def hard_close_out(self) -> bool:
        """Rule 203(b)(3): threshold securities must be closed out by T+13."""
        return self.days_outstanding >= 13
