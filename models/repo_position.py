from dataclasses import dataclass
from datetime import date
from .enums import SecurityType, AccountType


@dataclass
class RepoPosition:
    repo_id: str
    direction: str              # "REPO" (cash received) or "REVERSE" (cash paid)
    collateral_cusip: str
    collateral_market_value: float
    collateral_type: SecurityType
    cash_amount: float
    rate: float                 # Annualized repo rate (decimal)
    start_date: date
    end_date: date
    counterparty: str
    account_type: AccountType

    @property
    def is_repo(self) -> bool:
        return self.direction == "REPO"

    @property
    def is_reverse(self) -> bool:
        return self.direction == "REVERSE"

    @property
    def margin_excess(self) -> float:
        """Collateral MV minus cash — positive = overcollateralized."""
        return self.collateral_market_value - self.cash_amount
