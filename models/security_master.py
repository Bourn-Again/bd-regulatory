from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from .enums import SecurityType


@dataclass
class SecurityMaster:
    cusip: str
    description: str
    security_type: SecurityType
    asset_class: str          # equity / fixed_income / derivative
    price: float
    maturity_date: Optional[date] = None
    coupon: Optional[float] = None
    rating: Optional[str] = None   # e.g. "AAA", "BB+", "NR"
    currency: str = "USD"
    delta: Optional[float] = None
    gamma: Optional[float] = None
    vega: Optional[float] = None
    theta: Optional[float] = None

    def years_to_maturity(self, as_of: date) -> Optional[float]:
        if self.maturity_date is None:
            return None
        delta = (self.maturity_date - as_of).days
        return max(delta / 365.25, 0.0)
