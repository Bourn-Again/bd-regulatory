from dataclasses import dataclass
from datetime import date
from .enums import PositionSide, BusinessLine


@dataclass
class Position:
    position_id: str
    account_id: str
    cusip: str
    side: PositionSide
    quantity: float
    market_value: float     # Absolute value; sign determined by side
    cost_basis: float
    business_line: BusinessLine
    as_of_date: date

    @property
    def signed_market_value(self) -> float:
        return self.market_value if self.side == PositionSide.LONG else -self.market_value
