"""
analysis.py
Core CRM metrics: pipeline health, conversion rates, velocity, revenue forecast.
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIRECTORY = Path(__file__).parent.parent / "data"
PLOTS_DIRECTORY = Path(__file__).parent.parent / "plots"
PLOTS_DIRECTORY.mkdir(exist_ok=True)

STAGE_ORDER = ["Lead", "Qualified", "Demo", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
STAGE_WIN_PROBABILITY = {
    "Lead":        0.05,
    "Qualified":   0.15,
    "Demo":        0.30,
    "Proposal":    0.50,
    "Negotiation": 0.75,
    "Closed Won":  1.0,
    "Closed Lost": 0.0,
}


def pipeline_summary(deals_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Count, ACV, and weighted pipeline by stage."""
    open_deals = deals_dataframe[~deals_dataframe["stage"].isin(["Closed Won", "Closed Lost"])].copy()
    open_deals["win_probability"] = open_deals["stage"].map(STAGE_WIN_PROBABILITY)
    open_deals["weighted_acv"]    = open_deals["acv"] * open_deals["win_probability"]

    active_stages = [stage for stage in STAGE_ORDER if stage not in ("Closed Won", "Closed Lost")]
    summary_table = (
        open_deals.groupby("stage", observed=True)
        .agg(
            deal_count=("deal_id", "count"),
            total_acv=("acv", "sum"),
            weighted_acv=("weighted_acv", "sum"),
        )
        .reindex(active_stages)
        .dropna()
    )
    return summary_table


def conversion_rates(deals_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Stage-to-stage conversion rates."""
    active_deals  = deals_dataframe[deals_dataframe["stage"].isin(STAGE_ORDER)].copy()
    deals_per_stage = active_deals.groupby("stage")["deal_id"].count().reindex(STAGE_ORDER).fillna(0)

    conversion_list = []
    for stage_index in range(len(STAGE_ORDER) - 1):
        current_stage = STAGE_ORDER[stage_index]
        next_stage    = STAGE_ORDER[stage_index + 1]
        current_count = deals_per_stage[current_stage]
        next_count    = deals_per_stage[next_stage]
        conversion_rate = round(next_count / current_count, 4) if current_count > 0 else 0
        conversion_list.append({
            "from_stage":       current_stage,
            "to_stage":         next_stage,
            "conversion_rate":  conversion_rate,
        })
    return pd.DataFrame(conversion_list)


def win_rate_by_dimension(deals_dataframe: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Win rate broken down by any CRM dimension (region, industry, product, rep)."""
    closed_deals = deals_dataframe[deals_dataframe["stage"].isin(["Closed Won", "Closed Lost"])].copy()
    closed_deals["is_won"] = (closed_deals["stage"] == "Closed Won").astype(int)

    win_rate_table = (
        closed_deals.groupby(dimension)
        .agg(
            total_deals=("deal_id", "count"),
            total_wins=("is_won", "sum"),
            total_acv=("acv", "sum"),
        )
        .assign(
            win_rate=lambda table: table["total_wins"] / table["total_deals"],
            average_acv=lambda table: table["total_acv"] / table["total_deals"],
        )
        .sort_values("win_rate", ascending=False)
    )
    return win_rate_table


def sales_velocity(deals_dataframe: pd.DataFrame) -> pd.Series:
    """
    Sales velocity = (Deals × Win Rate × ACV) / Sales Cycle Length
    Computed per quarter.
    """
    deals_with_quarter = deals_dataframe.copy()
    deals_with_quarter["created_date"] = pd.to_datetime(deals_with_quarter["created_date"])
    deals_with_quarter["quarter"]      = deals_with_quarter["created_date"].dt.to_period("Q")

    closed_deals = deals_with_quarter[deals_with_quarter["stage"].isin(["Closed Won", "Closed Lost"])]
    won_deals    = deals_with_quarter[deals_with_quarter["stage"] == "Closed Won"]

    velocity_by_quarter = {}
    for quarter_period in sorted(deals_with_quarter["quarter"].unique()):
        closed_this_quarter = closed_deals[closed_deals["quarter"] == quarter_period]
        won_this_quarter    = won_deals[won_deals["quarter"] == quarter_period]

        if len(closed_this_quarter) == 0:
            continue

        number_of_deals      = len(closed_this_quarter)
        win_rate             = len(won_this_quarter) / number_of_deals if number_of_deals > 0 else 0
        average_deal_value   = won_this_quarter["acv"].mean() if len(won_this_quarter) > 0 else 0
        average_cycle_length = closed_this_quarter["days_in_pipeline"].mean() or 1

        velocity_by_quarter[str(quarter_period)] = round(
            (number_of_deals * win_rate * average_deal_value) / average_cycle_length, 0
        )
    return pd.Series(velocity_by_quarter, name="sales_velocity")


def revenue_forecast(deals_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    3-scenario revenue forecast for the next 4 quarters.
    Base: weighted pipeline. Bear: -25%. Bull: +20%.
    """
    open_deals = deals_dataframe[~deals_dataframe["stage"].isin(["Closed Won", "Closed Lost"])].copy()
    open_deals["win_probability"] = open_deals["stage"].map(STAGE_WIN_PROBABILITY)
    open_deals["weighted_acv"]    = open_deals["acv"] * open_deals["win_probability"]

    quarterly_base_revenue = open_deals["weighted_acv"].sum() / 4   # spread over 4 quarters
    quarterly_growth_rate  = 0.04                                    # 4% growth per quarter

    forecast_rows = []
    for quarter_index, quarter_label in enumerate(["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"]):
        growth_multiplier = 1 + quarterly_growth_rate * quarter_index
        forecast_rows.append({
            "quarter":    quarter_label,
            "bear_case":  int(quarterly_base_revenue * growth_multiplier * 0.75),
            "base_case":  int(quarterly_base_revenue * growth_multiplier),
            "bull_case":  int(quarterly_base_revenue * growth_multiplier * 1.20),
        })
    return pd.DataFrame(forecast_rows)


def rep_leaderboard(deals_dataframe: pd.DataFrame, targets_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Rep-level summary: won ACV, quota attainment, avg deal size, win rate."""
    won_deals_by_rep = deals_dataframe[deals_dataframe["stage"] == "Closed Won"].groupby("rep_name").agg(
        won_deal_count=("deal_id", "count"),
        total_won_acv=("acv", "sum"),
        average_deal_size=("acv", "mean"),
    )

    closed_deals = deals_dataframe[deals_dataframe["stage"].isin(["Closed Won", "Closed Lost"])]
    win_rate_per_rep = closed_deals.groupby("rep_name").apply(
        lambda rep_deals: (rep_deals["stage"] == "Closed Won").sum() / len(rep_deals),
        include_groups=False,
    ).rename("win_rate")

    annual_quota_per_rep = (
        targets_dataframe.groupby("rep_name")["quota"]
        .sum()
        .rename("annual_quota")
    )

    leaderboard = won_deals_by_rep.join(win_rate_per_rep).join(annual_quota_per_rep)
    leaderboard["quota_attainment"] = leaderboard["total_won_acv"] / leaderboard["annual_quota"]

    return leaderboard.sort_values("total_won_acv", ascending=False).round(2)