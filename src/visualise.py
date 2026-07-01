"""
visualise.py
Dark-themed matplotlib/seaborn charts for the CRM pipeline analysis.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

PLOTS_DIR = Path(__file__).parent.parent / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

BG     = "#0d1117"
PANEL  = "#161b22"
BORDER = "#30363d"
TEXT   = "#c9d1d9"
TITLE  = "#f0f6fc"
BLUE   = "#58a6ff"
GREEN  = "#2ecc71"
RED    = "#e74c3c"
AMBER  = "#f39c12"
PURPLE = "#a371f7"

PALETTE = [BLUE, GREEN, AMBER, RED, PURPLE, "#ec6547", "#63b3ed"]


def _ax(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=TEXT, labelsize=9)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER)
    ax.title.set_color(TITLE)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)


def _fig(w=14, h=6):
    fig = plt.figure(figsize=(w, h))
    fig.patch.set_facecolor(BG)
    return fig


def _save(name):
    path = PLOTS_DIR / name
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"path: {path}")



def plot_pipeline_funnel(summary: pd.DataFrame):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)
    _ax(ax1); _ax(ax2)

    stages = summary.index.tolist()
    acv    = summary["total_acv"].values / 1e6

    bars = ax1.barh(stages[::-1], acv[::-1], color=BLUE, alpha=0.85)
    ax1.bar_label(bars, fmt="$%.1fM", color=TEXT, padding=4, fontsize=9)
    ax1.set_title("Pipeline ACV by Stage", fontsize=13)
    ax1.set_xlabel("Total ACV ($M)")
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))

    w_acv = summary["weighted_acv"].values / 1e6
    bars2 = ax2.barh(stages[::-1], w_acv[::-1], color=GREEN, alpha=0.85)
    ax2.bar_label(bars2, fmt="$%.1fM", color=TEXT, padding=4, fontsize=9)
    ax2.set_title("Weighted Pipeline (Prob-Adjusted ACV)", fontsize=13)
    ax2.set_xlabel("Weighted ACV ($M)")
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))

    plt.tight_layout()
    _save("pipeline_funnel.png")

def plot_conversion_waterfall(conv: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor(BG); _ax(ax)

    stages = conv["from_stage"].tolist()
    rates  = (conv["conversion_rate"] * 100).tolist()
    colors = [GREEN if r >= 40 else AMBER if r >= 20 else RED for r in rates]

    bars = ax.bar(range(len(stages)), rates, color=colors, alpha=0.85, width=0.6)
    ax.bar_label(bars, fmt="%.1f%%", color=TEXT, padding=4, fontsize=10)
    ax.set_xticks(range(len(stages)))
    ax.set_xticklabels([f"{s}\n→ {conv['to_stage'].iloc[i]}" for i, s in enumerate(stages)], fontsize=9)
    ax.set_ylim(0, max(rates) * 1.25)
    ax.set_title("Stage-to-Stage Conversion Rates", fontsize=13)
    ax.set_ylabel("Conversion Rate (%)")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    plt.tight_layout()
    _save("conversion_waterfall.png")


def plot_revenue_forecast(forecast: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(BG); _ax(ax)

    x = range(len(forecast))
    ax.fill_between(x, forecast["bear_case"]/1e6, forecast["bull_case"]/1e6,
                    alpha=0.15, color=BLUE, label="Bear–Bull Range")
    ax.plot(x, forecast["base_case"]/1e6, color=BLUE,  lw=2.5, marker="o", ms=7, label="Base Case")
    ax.plot(x, forecast["bear_case"]/1e6, color=RED,   lw=1.5, ls="--", marker="s", ms=5, label="Bear Case (−25%)")
    ax.plot(x, forecast["bull_case"]/1e6, color=GREEN, lw=1.5, ls="--", marker="^", ms=5, label="Bull Case (+20%)")

    for i, row in forecast.iterrows():
        ax.annotate(f"${row['base_case']/1e6:.1f}M",
                    (i, row["base_case"]/1e6), textcoords="offset points",
                    xytext=(0, 12), ha="center", color=BLUE, fontsize=10)

    ax.set_xticks(list(x))
    ax.set_xticklabels(forecast["quarter"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"${y:.1f}M"))
    ax.set_title("Revenue Forecast — 3-Scenario Model (2025)", fontsize=13)
    ax.set_ylabel("Forecasted Revenue ($M)")
    ax.legend(facecolor=PANEL, labelcolor=TEXT, framealpha=0.9)
    plt.tight_layout()
    _save("revenue_forecast.png")


def plot_win_rates(wr_region: pd.DataFrame, wr_industry: pd.DataFrame):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor(BG); _ax(ax1); _ax(ax2)

    for ax, df, title in [(ax1, wr_region, "Win Rate by Region"),
                           (ax2, wr_industry, "Win Rate by Industry")]:
        rates = (df["win_rate"] * 100).sort_values()
        colors = [GREEN if r >= 55 else AMBER if r >= 40 else RED for r in rates]
        bars = ax.barh(rates.index, rates.values, color=colors, alpha=0.85)
        ax.bar_label(bars, fmt="%.1f%%", color=TEXT, padding=4, fontsize=9)
        ax.set_title(title, fontsize=12)
        ax.set_xlabel("Win Rate (%)")
        ax.set_xlim(0, rates.max() * 1.3)

    plt.tight_layout()
    _save("win_rates.png")

def plot_sales_velocity(velocity: pd.Series):
    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor(BG); _ax(ax)

    ax.plot(range(len(velocity)), velocity.values, color=PURPLE, lw=2, marker="o", ms=5)
    ax.fill_between(range(len(velocity)), velocity.values, alpha=0.2, color=PURPLE)

    # Trend line
    z = np.polyfit(range(len(velocity)), velocity.values, 1)
    p = np.poly1d(z)
    ax.plot(range(len(velocity)), p(range(len(velocity))),
            ls="--", color=AMBER, lw=1.5, label=f"Trend ({z[0]:+.0f}/qtr)")

    ax.set_xticks(range(len(velocity)))
    ax.set_xticklabels(velocity.index, rotation=45, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"${y:,.0f}"))
    ax.set_title("Sales Velocity by Quarter", fontsize=13)
    ax.set_ylabel("Velocity ($ / day)")
    ax.legend(facecolor=PANEL, labelcolor=TEXT)
    plt.tight_layout()
    _save("sales_velocity.png")


def plot_rep_leaderboard(board: pd.DataFrame):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.patch.set_facecolor(BG)
    for ax in axes: _ax(ax)

    metrics = [
        ("total_won_acv",        "Won ACV ($)",        BLUE,  True,  "$,.0f"),
        ("quota_attainment",     "Quota Attainment",    GREEN, False, ".0%"),
        ("average_deal_size",  "Avg Deal Size ($)",   AMBER, True,  "$,.0f"),
    ]
    for ax, (col, label, color, is_dollar, fmt) in zip(axes, metrics):
        vals = board[col].sort_values()
        bars = ax.barh(vals.index, vals.values, color=color, alpha=0.85)
        ax.set_title(label, fontsize=11)
        if is_dollar:
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e3:.0f}K"))
        else:
            ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))

    plt.tight_layout()
    _save("rep_leaderboard.png")


def plot_lead_source(df: pd.DataFrame):
    won = df[df["stage"] == "Closed Won"]
    src = won.groupby("lead_source")["acv"].agg(["sum","count"]).sort_values("sum", ascending=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor(BG); _ax(ax1); _ax(ax2)

    bars = ax1.bar(src.index, src["sum"]/1e6, color=PALETTE[:len(src)], alpha=0.85)
    ax1.bar_label(bars, fmt="$%.1fM", color=TEXT, padding=3, fontsize=9)
    ax1.set_title("Won ACV by Lead Source", fontsize=12)
    ax1.set_ylabel("Won ACV ($M)")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"${y:.0f}M"))

    ax2.pie(src["count"], labels=src.index, colors=PALETTE[:len(src)],
            autopct="%1.1f%%", textprops={"color": TEXT}, startangle=90,
            wedgeprops={"edgecolor": BG, "linewidth": 2})
    ax2.set_title("Deal Volume by Lead Source", fontsize=12)

    plt.tight_layout()
    _save("lead_source.png")