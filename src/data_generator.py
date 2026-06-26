"""
data_generator.py
Generates a realistic B2B SaaS CRM sales pipeline dataset (2022-2024).
"""

import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIRECTORY = Path(__file__).parent.parent / "data"
DATA_DIRECTORY.mkdir(exist_ok=True)

np.random.seed(42)

PIPELINE_STAGES = ["Lead", "Qualified", "Demo", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]

STAGE_WIN_PROBABILITY = {
    "Lead":        0.05,
    "Qualified":   0.15,
    "Demo":        0.30,
    "Proposal":    0.50,
    "Negotiation": 0.75,
}

STAGE_DURATION_DAYS = {
    "Lead":        (1,  30),
    "Qualified":   (5,  20),
    "Demo":        (7,  25),
    "Proposal":    (10, 30),
    "Negotiation": (5,  20),
}

INDUSTRY_LIST = ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Education", "Real Estate"]
INDUSTRY_DISTRIBUTION = [0.28, 0.18, 0.20, 0.12, 0.10, 0.07, 0.05]

REGION_LIST = ["North America", "Europe", "APAC", "LATAM"]
REGION_DISTRIBUTION = [0.45, 0.28, 0.18, 0.09]

SALES_REPS = [
    ("Alice Morgan",   "North America", "Enterprise"),
    ("Brian Chen",     "North America", "Mid-Market"),
    ("Carlos Rivera",  "LATAM",         "Mid-Market"),
    ("Diana Patel",    "Europe",        "Enterprise"),
    ("Ethan Park",     "APAC",          "SMB"),
    ("Fiona Walsh",    "Europe",        "SMB"),
    ("George Kim",     "North America", "Enterprise"),
    ("Hannah Brooks",  "APAC",          "Mid-Market"),
]

PRODUCT_LIST = ["CRM Pro", "CRM Enterprise", "Analytics Add-on", "Integration Suite", "Support Plus"]
PRODUCT_ACV_RANGE = {
    "CRM Pro":           (8000,  25000),
    "CRM Enterprise":    (40000, 200000),
    "Analytics Add-on":  (5000,  15000),
    "Integration Suite": (12000, 45000),
    "Support Plus":      (3000,  10000),
}

LEAD_SOURCE_LIST = ["Inbound", "Outbound", "Referral", "Event", "Partner", "Paid Search"]
LEAD_SOURCE_DISTRIBUTION = [0.30, 0.22, 0.18, 0.12, 0.10, 0.08]


def generate_deals(number_of_deals: int = 1200) -> pd.DataFrame:
    all_deal_rows = []
    pipeline_start_date = pd.Timestamp("2022-01-01")
    pipeline_end_date   = pd.Timestamp("2024-12-31")
    total_date_range    = (pipeline_end_date - pipeline_start_date).days

    for deal_index in range(number_of_deals):
        rep_name, rep_region, rep_segment = SALES_REPS[deal_index % len(SALES_REPS)]
        industry     = np.random.choice(INDUSTRY_LIST, p=INDUSTRY_DISTRIBUTION)
        product      = np.random.choice(PRODUCT_LIST)
        acv_min, acv_max = PRODUCT_ACV_RANGE[product]
        deal_acv     = int(np.random.uniform(acv_min, acv_max) / 500) * 500
        lead_source  = np.random.choice(LEAD_SOURCE_LIST, p=LEAD_SOURCE_DISTRIBUTION)
        created_date = pipeline_start_date + pd.Timedelta(
            days=int(np.random.uniform(0, total_date_range - 180))
        )

        # Walk the deal through each pipeline stage
        current_date  = created_date
        stage_history = []
        reached_stage = "Lead"

        for stage_name in PIPELINE_STAGES[:-2]:
            min_days, max_days = STAGE_DURATION_DAYS[stage_name]
            days_spent_in_stage = int(np.random.uniform(min_days, max_days))
            stage_history.append((stage_name, current_date))
            current_date += pd.Timedelta(days=days_spent_in_stage)

            advancement_threshold = STAGE_WIN_PROBABILITY[stage_name] * 1.8
            deal_did_not_advance  = np.random.random() > advancement_threshold
            if deal_did_not_advance:
                reached_stage = stage_name
                break
            reached_stage = stage_name

        # Determine final outcome
        deal_reached_negotiation = reached_stage == "Negotiation"
        deal_progressed_far      = reached_stage != "Lead" and np.random.random() < 0.55
        if deal_reached_negotiation or deal_progressed_far:
            final_outcome = "Closed Won" if np.random.random() < 0.62 else "Closed Lost"
        else:
            final_outcome = np.random.choice(
                ["Closed Lost", reached_stage], p=[0.25, 0.75]
            )

        deal_is_closed = final_outcome in ("Closed Won", "Closed Lost")
        close_date = (
            current_date + pd.Timedelta(days=int(np.random.uniform(5, 30)))
            if deal_is_closed else None
        )

        deal_score = round(np.random.uniform(20, 95), 1)

        all_deal_rows.append({
            "deal_id":           f"DL-{10000 + deal_index}",
            "deal_name":         f"{industry} Corp #{deal_index + 1}",
            "rep_name":          rep_name,
            "rep_segment":       rep_segment,
            "region":            rep_region,
            "industry":          industry,
            "product":           product,
            "lead_source":       lead_source,
            "acv":               deal_acv,
            "stage":             final_outcome if deal_is_closed else reached_stage,
            "created_date":      created_date.date(),
            "close_date":        close_date.date() if close_date else None,
            "days_in_pipeline":  (current_date - created_date).days,
            "deal_score":        deal_score,
            "num_touches":       int(np.random.uniform(3, 40)),
            "competitors":       np.random.choice(
                ["Salesforce", "HubSpot", "Microsoft", "None", "Zoho"],
                p=[0.25, 0.20, 0.18, 0.22, 0.15],
            ),
            "forecast_category": np.random.choice(
                ["Pipeline", "Best Case", "Commit", "Closed"],
                p=[0.35, 0.25, 0.20, 0.20],
            ),
        })

    deals_dataframe = pd.DataFrame(all_deal_rows)
    deals_dataframe.to_csv(DATA_DIRECTORY / "crm_deals.csv", index=False)
    print(f"Generated {len(deals_dataframe)} deals  →  data/crm_deals.csv")
    return deals_dataframe


def generate_activities(deals_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Generate a call/email/meeting activity log linked to deals."""
    ACTIVITY_TYPE_LIST = ["Call", "Email", "Demo", "Meeting", "Proposal Sent", "Follow-up"]
    all_activity_rows = []

    for _, deal_row in deals_dataframe.iterrows():
        number_of_activities = int(np.random.uniform(2, deal_row["num_touches"]))
        deal_start_date      = pd.Timestamp(deal_row["created_date"])

        for activity_index in range(number_of_activities):
            activity_date = deal_start_date + pd.Timedelta(
                days=int(np.random.uniform(0, 120))
            )
            all_activity_rows.append({
                "activity_id":   f"ACT-{len(all_activity_rows) + 1:06d}",
                "deal_id":       deal_row["deal_id"],
                "rep_name":      deal_row["rep_name"],
                "activity_type": np.random.choice(ACTIVITY_TYPE_LIST),
                "activity_date": activity_date.date(),
                "duration_min":  int(np.random.choice(
                    [15, 30, 45, 60, 90], p=[0.10, 0.35, 0.20, 0.25, 0.10]
                )),
                "outcome":       np.random.choice(
                    ["Positive", "Neutral", "Negative"], p=[0.50, 0.35, 0.15]
                ),
            })

    activities_dataframe = pd.DataFrame(all_activity_rows)
    activities_dataframe.to_csv(DATA_DIRECTORY / "crm_activities.csv", index=False)
    print(f"✅ Generated {len(activities_dataframe)} activities  →  data/crm_activities.csv")
    return activities_dataframe


def generate_monthly_targets() -> pd.DataFrame:
    """Monthly quota targets per rep."""
    rep_name_list  = [rep[0] for rep in SALES_REPS]
    all_months     = pd.date_range("2022-01", "2024-12", freq="MS")
    all_target_rows = []

    for rep_name in rep_name_list:
        base_quota_amount = np.random.choice([80000, 120000, 150000, 200000])

        for month_date in all_months:
            months_since_start = (month_date.year - 2022) * 12 + month_date.month - 1
            growth_multiplier  = 1 + 0.02 * months_since_start / 12
            monthly_quota      = int(base_quota_amount * growth_multiplier / 1000) * 1000
            attainment_rate    = round(np.random.uniform(0.55, 1.35), 2)

            all_target_rows.append({
                "rep_name":   rep_name,
                "month":      month_date.date(),
                "quota":      monthly_quota,
                "attainment": attainment_rate,
            })

    targets_dataframe = pd.DataFrame(all_target_rows)
    targets_dataframe["actual"] = (
        targets_dataframe["quota"] * targets_dataframe["attainment"]
    ).astype(int)

    targets_dataframe.to_csv(DATA_DIRECTORY / "monthly_targets.csv", index=False)
    print(f" Generated monthly targets  →  data/monthly_targets.csv")
    return targets_dataframe