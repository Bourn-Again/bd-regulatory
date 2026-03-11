"""
Scenario Engine: apply hypothetical trades to the BookOfRecord
and recompute regulatory metrics to show before/after impact.
"""
from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from typing import List

import config
from models.book_of_record import BookOfRecord
from models.position import Position
from models.security_master import SecurityMaster
from models.enums import PositionSide, BusinessLine, SecurityType


@dataclass
class ScenarioTrade:
    trade_id: str
    account_id: str
    client_name: str
    cusip: str
    description: str
    direction: str          # "BUY" or "SELL"
    quantity: float
    price: float
    security_type: str
    asset_class: str        # equity / fixed_income / derivative
    is_margin: bool = True

    @property
    def market_value(self) -> float:
        if self.security_type == "OPTION":
            return abs(self.quantity) * 100 * self.price
        elif self.asset_class == "fixed_income":
            return abs(self.quantity) * (self.price / 100.0)
        else:
            return abs(self.quantity) * self.price

    @property
    def side(self) -> PositionSide:
        return PositionSide.LONG if self.direction == "BUY" else PositionSide.SHORT

    @property
    def notional_label(self) -> str:
        if self.security_type == "OPTION":
            return f"{self.quantity:,.0f} contracts"
        elif self.asset_class == "fixed_income":
            return f"${self.quantity:,.0f} face"
        else:
            return f"{self.quantity:,.0f} shares"


def new_trade_id() -> str:
    return uuid.uuid4().hex[:8].upper()


def apply_scenario(bor: BookOfRecord, trades: List[ScenarioTrade]) -> BookOfRecord:
    """
    Return a new BookOfRecord with all scenario trades applied.
    Copies accounts (so originals are unmodified) and appends new positions.
    """
    if not trades:
        return bor

    new_accounts   = {k: copy.copy(v) for k, v in bor.accounts.items()}
    new_positions  = list(bor.positions)
    new_securities = dict(bor.securities)

    for i, trade in enumerate(trades):
        mv = trade.market_value

        # Register security if not already in master
        if trade.cusip not in new_securities:
            new_securities[trade.cusip] = SecurityMaster(
                cusip=trade.cusip,
                description=trade.description,
                security_type=SecurityType(trade.security_type),
                asset_class=trade.asset_class,
                price=trade.price,
            )

        # Add position
        new_positions.append(Position(
            position_id=f"SCN_{i:04d}_{trade.trade_id}",
            account_id=trade.account_id,
            cusip=trade.cusip,
            side=trade.side,
            quantity=trade.quantity,
            market_value=mv,
            cost_basis=mv,
            business_line=BusinessLine.PRIME_BROKERAGE,
            as_of_date=config.CALCULATION_DATE,
        ))

        # Update account aggregates
        if trade.account_id in new_accounts:
            acct = new_accounts[trade.account_id]
            if trade.direction == "BUY":
                acct.long_market_value += mv
                if trade.is_margin:
                    acct.margin_debit += mv * config.REG_T_INITIAL_MARGIN
            else:
                acct.short_market_value += mv

    # Invalidate cached dataframes on new BOR
    new_bor = BookOfRecord(
        securities=new_securities,
        accounts=new_accounts,
        positions=new_positions,
        repo_positions=bor.repo_positions,
        firm_balance_sheet=bor.firm_balance_sheet,
    )
    return new_bor
