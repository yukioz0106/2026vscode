"""
経営KPI算出モジュール
経営企画部 KPI一覧（KPI定義/KPI一覧.md）に基づき、財務データからKPIを算出する。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FinancialData:
    fiscal_year: str
    quarter: str
    # P/L
    revenue: float
    operating_profit: float
    net_income: float
    depreciation: float
    tax_rate: float = 0.30
    # B/S（期末値）
    equity: float = 0.0
    equity_prior: float = 0.0  # 前期末自己資本（期中平均ROE計算用）
    interest_bearing_debt: float = 0.0
    total_assets: float = 0.0
    # CF
    operating_cf: float = 0.0
    investing_cf: float = 0.0
    shareholder_return: float = 0.0
    # 株式
    shares_outstanding: float = 0.0
    dividend_per_share: float = 0.0


class KPICalculator:
    """財務KPI算出クラス（KPI一覧.md F-01〜F-10対応）"""

    def __init__(self, data: FinancialData):
        self.d = data

    # F-01: 期中平均自己資本で計算（有価証券報告書開示値と一致）
    def roe(self) -> Optional[float]:
        if self.d.equity_prior > 0:
            avg_equity = (self.d.equity_prior + self.d.equity) / 2
        else:
            avg_equity = self.d.equity
        if avg_equity == 0:
            return None
        return self.d.net_income / avg_equity * 100

    # F-02
    def roic(self) -> Optional[float]:
        invested_capital = self.d.interest_bearing_debt + self.d.equity
        if invested_capital == 0:
            return None
        nopat = self.d.operating_profit * (1 - self.d.tax_rate)
        return nopat / invested_capital * 100

    # F-03
    def ebitda(self) -> float:
        return self.d.operating_profit + self.d.depreciation

    # F-04
    def free_cash_flow(self) -> float:
        return self.d.operating_cf + self.d.investing_cf

    # F-05
    def de_ratio(self) -> Optional[float]:
        if self.d.equity == 0:
            return None
        return self.d.interest_bearing_debt / self.d.equity

    # F-06
    def revenue(self) -> float:
        return self.d.revenue

    # F-07
    def net_income(self) -> float:
        return self.d.net_income

    # F-08
    def eps(self) -> Optional[float]:
        if self.d.shares_outstanding == 0:
            return None
        return self.d.net_income / self.d.shares_outstanding

    # F-09
    def payout_ratio(self) -> Optional[float]:
        eps = self.eps()
        if eps is None or eps == 0:
            return None
        return self.d.dividend_per_share / eps * 100

    # F-10
    def shareholder_return(self) -> float:
        return self.d.shareholder_return

    def all_kpis(self) -> dict:
        return {
            "fiscal_year": self.d.fiscal_year,
            "quarter": self.d.quarter,
            "F01_roe": self.roe(),
            "F02_roic": self.roic(),
            "F03_ebitda": self.ebitda(),
            "F04_fcf": self.free_cash_flow(),
            "F05_de_ratio": self.de_ratio(),
            "F06_revenue": self.revenue(),
            "F07_net_income": self.net_income(),
            "F08_eps": self.eps(),
            "F09_payout_ratio": self.payout_ratio(),
            "F10_shareholder_return": self.shareholder_return(),
        }


class PlanVsActualAnalyzer:
    """計画値 vs 実績値の差異分析"""

    def variance(self, actual: float, plan: float) -> dict:
        diff = actual - plan
        rate = (diff / plan * 100) if plan != 0 else None
        return {"actual": actual, "plan": plan, "diff": diff, "diff_rate_pct": rate}

    def achievement_rate(self, actual: float, plan: float) -> Optional[float]:
        if plan == 0:
            return None
        return actual / plan * 100
