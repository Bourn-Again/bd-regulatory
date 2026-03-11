"""
Reg SHO (Rule 203/204) — Fails-to-Deliver / Fails-to-Receive tracking.
Monitors aging of settlement fails, close-out obligations, and locate coverage.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict

import config
from models.book_of_record import BookOfRecord
from models.fail_position import FailPosition


@dataclass
class AgingBucket:
    label: str
    count: int
    market_value: float
    ftr_count: int
    ftd_count: int
    ftr_mv: float
    ftd_mv: float


@dataclass
class FailsSummary:
    # Totals
    total_fails: int
    total_ftr: int
    total_ftd: int
    total_ftr_mv: float
    total_ftd_mv: float
    net_fail_exposure: float    # FTD mv - FTR mv (net delivery obligation)

    # Aging
    aging_buckets: List[AgingBucket]

    # Obligation flags
    close_out_required: List[FailPosition]    # T+3+: must buy-in per Rule 204
    hard_close_out: List[FailPosition]         # T+13+: threshold securities

    # All records
    fail_records: List[FailPosition]

    # By business line
    by_business_line: Dict[str, float]

    # Reg SHO compliance
    is_compliant: bool   # False if any hard_close_out items exist
    open_close_out_mv: float
    open_hard_close_out_mv: float


class FailsCalculator:
    BUCKET_LABELS = ["T+1", "T+2", "T+3", "T+4–13", "T+13+"]

    def __init__(self, bor: BookOfRecord, fails: List[FailPosition],
                 as_of: date = None):
        self.bor   = bor
        self.fails = fails
        self.as_of = as_of or config.CALCULATION_DATE

    def calculate(self) -> FailsSummary:
        ftrs = [f for f in self.fails if f.direction == "FTR"]
        ftds = [f for f in self.fails if f.direction == "FTD"]

        ftr_mv = sum(f.market_value for f in ftrs)
        ftd_mv = sum(f.market_value for f in ftds)

        # Aging buckets
        bucket_data: Dict[str, Dict] = {
            lbl: {"count": 0, "mv": 0.0, "ftr_c": 0, "ftd_c": 0,
                  "ftr_mv": 0.0, "ftd_mv": 0.0}
            for lbl in self.BUCKET_LABELS
        }
        for f in self.fails:
            b = bucket_data[f.aging_bucket]
            b["count"] += 1
            b["mv"]    += f.market_value
            if f.direction == "FTR":
                b["ftr_c"]  += 1
                b["ftr_mv"] += f.market_value
            else:
                b["ftd_c"]  += 1
                b["ftd_mv"] += f.market_value

        buckets = [
            AgingBucket(
                label=lbl,
                count=d["count"],
                market_value=d["mv"],
                ftr_count=d["ftr_c"],
                ftd_count=d["ftd_c"],
                ftr_mv=d["ftr_mv"],
                ftd_mv=d["ftd_mv"],
            )
            for lbl, d in bucket_data.items()
        ]

        close_outs  = [f for f in self.fails if f.close_out_required]
        hard_close  = [f for f in self.fails if f.hard_close_out]

        by_bline: Dict[str, float] = {}
        for f in self.fails:
            by_bline[f.business_line] = by_bline.get(f.business_line, 0) + f.market_value

        return FailsSummary(
            total_fails=len(self.fails),
            total_ftr=len(ftrs),
            total_ftd=len(ftds),
            total_ftr_mv=ftr_mv,
            total_ftd_mv=ftd_mv,
            net_fail_exposure=ftd_mv - ftr_mv,
            aging_buckets=buckets,
            close_out_required=close_outs,
            hard_close_out=hard_close,
            fail_records=self.fails,
            by_business_line=by_bline,
            is_compliant=len(hard_close) == 0,
            open_close_out_mv=sum(f.market_value for f in close_outs),
            open_hard_close_out_mv=sum(f.market_value for f in hard_close),
        )
