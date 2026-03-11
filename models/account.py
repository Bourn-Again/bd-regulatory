from dataclasses import dataclass, field
from .enums import AccountType, BusinessLine


@dataclass
class Account:
    account_id: str
    account_type: AccountType
    business_line: BusinessLine
    cash_balance: float
    margin_debit: float
    short_market_value: float
    long_market_value: float
    is_margin_account: bool
    is_prime_brokerage: bool
    client_name: str = ""

    @property
    def equity(self) -> float:
        return self.long_market_value - self.short_market_value - self.margin_debit
