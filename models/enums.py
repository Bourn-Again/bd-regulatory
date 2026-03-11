from enum import Enum, auto


class SecurityType(Enum):
    US_TREASURY = "US_TREASURY"
    AGENCY = "AGENCY"
    MUNICIPAL = "MUNICIPAL"
    CORP_IG = "CORP_IG"
    CORP_HY = "CORP_HY"
    EQUITY_LISTED = "EQUITY_LISTED"
    EQUITY_OTC = "EQUITY_OTC"
    MBS = "MBS"
    CMO = "CMO"
    OPTION = "OPTION"
    ETF = "ETF"
    REPO_COLLATERAL = "REPO_COLLATERAL"
    NON_MARKETABLE = "NON_MARKETABLE"


class AccountType(Enum):
    CUSTOMER = "CUSTOMER"
    FIRM = "FIRM"
    PAB = "PAB"      # Proprietary Accounts of Broker-Dealers


class BusinessLine(Enum):
    PRIME_BROKERAGE = "PRIME_BROKERAGE"
    MARKET_MAKING = "MARKET_MAKING"
    REPO = "REPO"
    INSTITUTIONAL_EQUITY = "INSTITUTIONAL_EQUITY"
    INST_FIXED_INCOME = "INST_FIXED_INCOME"


class PositionSide(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
