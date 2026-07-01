"""
main.py  ─  CRM Sales Pipeline & Revenue Forecasting
End-to-end runner: generates data, analysis, charts, Excel workbook, Tableau export.
"""

import sys
sys.path.insert(0, ".")

from src.data_generator import generate_deals, generate_activities, generate_monthly_targets
from src.analysis import (
    pipeline_summary, conversion_rates, win_rate_by_dimension,
    sales_velocity, revenue_forecast, rep_leaderboard,
)
from src.visualise import (
    plot_pipeline_funnel, plot_conversion_waterfall, plot_revenue_forecast,
    plot_win_rates, plot_sales_velocity, plot_rep_leaderboard, plot_lead_source,
)
from src.excel_builder import build_excel


def main():
    print("\n" + "═" * 60)
    print("  CRM Sales Pipeline & Revenue Forecasting")
    print("═" * 60 + "\n")

    # ── 1. Generate data ──────────────────────────────────────────
    print("[ 1 / 4 ]  Generating CRM dataset …")
    deals      = generate_deals(n=1200)
    activities = generate_activities(deals)
    targets    = generate_monthly_targets()

    # ── 2. Analysis ───────────────────────────────────────────────
    print("\n[ 2 / 4 ]  Running analysis …")
    summary    = pipeline_summary(deals)
    conv       = conversion_rates(deals)
    wr_region  = win_rate_by_dimension(deals, "region")
    wr_industry= win_rate_by_dimension(deals, "industry")
    velocity   = sales_velocity(deals)
    forecast   = revenue_forecast(deals)
    board      = rep_leaderboard(deals, targets)

    print("\n  Pipeline Summary:")
    print(summary.to_string())
    print(f"\n  Revenue Forecast:")
    print(forecast.to_string(index=False))

    # ── 3. Charts ─────────────────────────────────────────────────
    print("\n[ 3 / 4 ]  Generating charts …")
    plot_pipeline_funnel(summary)
    plot_conversion_waterfall(conv)
    plot_revenue_forecast(forecast)
    plot_win_rates(wr_region, wr_industry)
    plot_sales_velocity(velocity)
    plot_rep_leaderboard(board)
    plot_lead_source(deals)

    # ── 4. Excel workbook ─────────────────────────────────────────
    print("\n[ 4 / 4 ]  Building Excel workbook …")
    build_excel(deals, forecast, board, targets, activities)

    print("\n✅  All done!")
    print("   📁 data/            → CSVs + Excel workbook")
    print("   📊 plots/           → 7 analysis charts")
    print("   📤 Tableau Export   → Sheet 4 in Excel (or data/crm_deals.csv)")


if __name__ == "__main__":
    main()
