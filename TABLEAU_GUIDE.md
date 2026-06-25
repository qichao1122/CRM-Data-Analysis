# Tableau Dashboard Setup Guide

This guide walks you through connecting the CRM data to Tableau and building the recommended dashboards.

## Step 1: Connect to Data

1. Open Tableau Desktop (or Tableau Public)
2. Click **Connect → Microsoft Excel**
3. Select `data/CRM_Sales_Pipeline.xlsx`
4. Drag the **📤 Tableau Export** sheet to the canvas
5. Click **Update Now** to preview

Alternatively, connect directly to `data/crm_deals.csv` via **Text File**.

---

## Step 2: Recommended Calculated Fields

Create these in Tableau (**Analysis → Create Calculated Field**):

### Win Rate
```
SUM(IF [Stage] = "Closed Won" THEN 1 ELSE 0 END) /
COUNT(IF [Stage] IN ("Closed Won", "Closed Lost") THEN [Deal Id] END)
```

### Weighted ACV (dynamic)
```
[Acv] * [Win Prob]
```

### Days Since Created
```
DATEDIFF('day', [Created Date], TODAY())
```

### Deal Size Tier
```
IF [Acv] >= 100000 THEN "Enterprise (100K+)"
ELSEIF [Acv] >= 25000 THEN "Mid-Market (25K–100K)"
ELSE "SMB (<25K)"
END
```

### Quota Attainment Color
```
IF [Attainment] >= 1.0 THEN "On Track"
ELSEIF [Attainment] >= 0.75 THEN "At Risk"
ELSE "Below Target"
END
```

---

## Step 3: Recommended Dashboards

### Dashboard 1 — Pipeline Overview
| Viz | Type | Details |
|-----|------|---------|
| Pipeline by Stage | Horizontal Bar | Dimension: Stage, Measure: SUM(ACV) |
| Weighted vs Unweighted | Dual Bar | Two measures on same chart |
| Pipeline Trend | Line Chart | Created Quarter on X, SUM(ACV) on Y |
| Deal Count Heatmap | Heatmap | Industry × Region |

### Dashboard 2 — Revenue Forecast
| Viz | Type | Details |
|-----|------|---------|
| 3-Scenario Forecast | Line Chart | Bear/Base/Bull on Y, Quarter on X |
| Forecast Category Mix | Stacked Bar | Pipeline / Best Case / Commit / Closed |
| Won ACV Over Time | Area Chart | Created Month on X, filter: Stage = Closed Won |

### Dashboard 3 — Rep Performance
| Viz | Type | Details |
|-----|------|---------|
| Rep Leaderboard | Bar Chart | Rep Name on Y, Won ACV on X, sorted desc |
| Win Rate by Rep | Bullet Chart | Actual vs target win rate |
| Activity Heatmap | Heatmap | Rep Name × Month, measure: Activity Count |
| Quota Attainment | KPI tiles | Color-coded by attainment tier |

### Dashboard 4 — Deal Intelligence
| Viz | Type | Details |
|-----|------|---------|
| Win Rate by Industry | Tree Map | Size: Won ACV, Color: Win Rate |
| Lead Source ROI | Scatter Plot | X: Deal Count, Y: Avg Won ACV |
| Competitor Analysis | Bar Chart | Competitor on Y, Win Rate on X |
| Deal Score Distribution | Histogram | Bin: Deal Score, Color: Stage |

---

## Step 4: Filters to Add (All Dashboards)

- **Date Range** (Created Date)
- **Region** (multi-select)
- **Rep Name** (multi-select)
- **Rep Segment** (Enterprise / Mid-Market / SMB)
- **Product** (multi-select)

---

## Step 5: Publish

- **Tableau Public**: File → Save to Tableau Public
- **Tableau Server/Cloud**: Server → Publish Workbook

> Tip: Schedule a daily extract refresh if connecting to a live CRM like Salesforce.
