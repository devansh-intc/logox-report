#!/usr/bin/env python3.11
"""
LogOX 4-Week Performance Report: Mar 2–29, 2026
Reads daily Shopify + Facebook CSVs and generates an HTML dashboard.
"""

import json
import pandas as pd
import os
from datetime import datetime

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(BASE, "../..")
FB_CSV   = os.path.join(BASE, "fb_mar2026_daily.csv")
SHOP_CSV = os.path.join(BASE, "sales_mar2026_daily.csv")
OUTPUT   = os.path.join(ROOT, "reports/LogOX/LogOX_Weekly_Performance_2026-03-31.html")
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

# ─── Triple Whale Hardcoded KPIs (from screenshots) ───────────────────────────
TW = {
    "W1": {"label":"W1 (Mar 2–8)",   "blended":41064.86,"spend":10028,"mer":0.33,"roas":3.04,"profit":3960, "margin":0.13,"ncpa":120.8,"nc_roas":2.98,"google":962.70, "meta":8028.98,"ms":111.90},
    "W2": {"label":"W2 (Mar 9–15)",  "blended":35564.79,"spend":8240, "mer":0.24,"roas":4.11,"profit":7589, "margin":0.22,"ncpa":100.5,"nc_roas":3.92,"google":2049.30,"meta":5489.82,"ms":525.39},
    "W3": {"label":"W3 (Mar 16–22)", "blended":37082.38,"spend":7078, "mer":0.22,"roas":4.49,"profit":7185, "margin":0.23,"ncpa":84.3, "nc_roas":4.34,"google":2549.76,"meta":4021.58,"ms":417.04},
    "W4": {"label":"W4 (Mar 23–29)", "blended":36135.95,"spend":7726, "mer":0.24,"roas":4.18,"profit":9400, "margin":0.29,"ncpa":72.9, "nc_roas":3.88,"google":2444.01,"meta":4077.53,"ms":315.17},
}
WEEKS = ["W1","W2","W3","W4"]

# ─── Week assignment ──────────────────────────────────────────────────────────
def assign_week(day_str):
    d = pd.to_datetime(day_str).day
    if   d <= 8:  return "W1"
    elif d <= 15: return "W2"
    elif d <= 22: return "W3"
    else:         return "W4"

# ─── Facebook URL → Product Category mapping ─────────────────────────────────
URL_MAP = {
    "pages/multitool":              "3-in-1 MultiTool",
    "products/logox-3-in-1":        "3-in-1 MultiTool",
    "products/forester-package":    "Forester Package",
    "products/timberox-ddl":        "TimberOX Dan-D-Lift",
    "products/timberox":            "TimberOX 30-Ton",
    "products/logox-carrying-tool": "LogOX Hauler",
    "products/carryox-gear-bag":    "CarryOX Gear Bag",
    "products/fireside-bundle":     "Fireside Bundle",
    "products/logox-firewood-hearth-bin": "Hearth Bin",
    "amazon.ca":                    "WoodOX Sling (Amazon)",
    "amazon.com":                   "WoodOX Sling (Amazon)",
}
CAT_ORDER = ["3-in-1 MultiTool","Forester Package","TimberOX 30-Ton","TimberOX Dan-D-Lift",
             "LogOX Hauler","CarryOX Gear Bag","Fireside Bundle","Hearth Bin","WoodOX Sling (Amazon)"]

def url_to_category(url):
    if not isinstance(url, str): return "Other"
    for key, cat in URL_MAP.items():
        if key in url: return cat
    return "Other"

# ─── Shopify product grouping ─────────────────────────────────────────────────
PROD_MAP = {
    "LogOX 3-in-1 Forestry MultiTool":             "3-in-1 MultiTool",
    "TimberOX Summit 30-Ton Log Splitter":          "TimberOX 30-Ton",
    "LogOX Forester Package":                       "Forester Package",
    "LogOX Hauler":                                 "LogOX Hauler",
    "TimberOX Summit Dan-D-Lift Manual Log Lift":   "TimberOX Dan-D-Lift",
    "The Woodsman Bundle":                          "Woodsman Bundle",
    "The LogOX Ultimate Bundle":                    "Ultimate Bundle",
    "TW Series 4-Way Wedge":                        "4-Way Wedge",
    "PickOX Pickaroon Attachment":                  "PickOX",
    "LogOX Forester Package Upgrade":               "Forester Upgrade",
    "CarryOX Gear Bag":                             "CarryOX Gear Bag",
}
def group_product(name):
    if not isinstance(name, str): return "Other"
    for k, v in PROD_MAP.items():
        if k in name: return v
    return "Other"

# ─── Load + process FB data ───────────────────────────────────────────────────
fb = pd.read_csv(FB_CSV)
fb["Week"]    = fb["Day"].apply(assign_week)
fb["Category"] = fb["Link (ad settings)"].apply(url_to_category)
fb_weekly = (fb.groupby(["Category","Week"])["Amount spent (USD)"]
               .sum().reset_index()
               .pivot(index="Category", columns="Week", values="Amount spent (USD)")
               .fillna(0).reindex(index=CAT_ORDER, fill_value=0))
fb_weekly["Total"] = fb_weekly[WEEKS].sum(axis=1)
fb_weekly = fb_weekly[fb_weekly["Total"] > 0]

# ─── Load + process Shopify data ─────────────────────────────────────────────
shop = pd.read_csv(SHOP_CSV)
shop = shop[shop["Product title"].notna() & (shop["Net sales"] > 0)].copy()
shop["Week"]    = shop["Day"].apply(assign_week)
shop["Product"] = shop["Product title"].apply(group_product)
shop_weekly = (shop.groupby(["Product","Week"])["Net sales"]
                   .sum().reset_index()
                   .pivot(index="Product", columns="Week", values="Net sales")
                   .fillna(0))
shop_weekly["Total"] = shop_weekly[WEEKS].sum(axis=1)
shop_weekly = shop_weekly.sort_values("Total", ascending=False)

# ─── Colors ───────────────────────────────────────────────────────────────────
BRAND_GREEN  = "#2D6A4F"
BRAND_ACCENT = "#52B788"
GOOGLE_BLUE  = "#4285F4"
META_BLUE    = "#1877F2"
MS_GRAY      = "#737373"
WEEK_COLORS  = ["#1B4332","#2D6A4F","#52B788","#95D5B2"]

def js_arr(vals):
    return "[" + ",".join(f"{v:.2f}" for v in vals) + "]"

def money(v):
    return f"${v:,.0f}"

def pct(v):
    return f"{v*100:.0f}%"

# ─── Build HTML ───────────────────────────────────────────────────────────────
labels_js = '["W1 (Mar 2–8)","W2 (Mar 9–15)","W3 (Mar 16–22)","W4 (Mar 23–29)"]'
google_vals = js_arr([TW[w]["google"] for w in WEEKS])
meta_vals   = js_arr([TW[w]["meta"]   for w in WEEKS])
ms_vals     = js_arr([TW[w]["ms"]     for w in WEEKS])
mer_vals    = js_arr([TW[w]["mer"]*100 for w in WEEKS])
roas_vals   = js_arr([TW[w]["roas"]   for w in WEEKS])
nc_roas_vals= js_arr([TW[w]["nc_roas"] for w in WEEKS])
profit_vals = js_arr([TW[w]["profit"] for w in WEEKS])
ncpa_vals   = js_arr([TW[w]["ncpa"]   for w in WEEKS])

# Meta spend by product JS datasets
fb_datasets_js = []
for i, cat in enumerate(fb_weekly.index):
    vals = js_arr([fb_weekly.loc[cat, w] if w in fb_weekly.columns else 0 for w in WEEKS])
    color = WEEK_COLORS[i % len(WEEK_COLORS)]
    fb_datasets_js.append(f'{{"label":"{cat}","data":{vals},"backgroundColor":"{color}","borderRadius":3}}')
fb_chart_js = "[" + ",".join(fb_datasets_js) + "]"

# Shopify net sales by product JS datasets (top 8)
top_products = shop_weekly.head(8)
shop_datasets_js = []
for i, prod in enumerate(top_products.index):
    vals = js_arr([top_products.loc[prod, w] if w in top_products.columns else 0 for w in WEEKS])
    color = WEEK_COLORS[i % len(WEEK_COLORS)]
    shop_datasets_js.append(f'{{"label":"{prod}","data":{vals},"backgroundColor":"{color}","borderRadius":3}}')
shop_chart_js = "[" + ",".join(shop_datasets_js) + "]"

# KPI summary table rows
def kpi_row(label, vals, fmt_fn, good="down"):
    cells = ""
    for i, w in enumerate(WEEKS):
        v = vals[i]
        cells += f'<td class="num">{fmt_fn(v)}</td>'
    # delta W1→W4
    d = vals[-1] - vals[0]
    arrow = "▲" if d > 0 else "▼"
    good_delta = (d < 0 and good == "down") or (d > 0 and good == "up")
    cls = "pos" if good_delta else "neg"
    cells += f'<td class="num delta {cls}">{arrow} {fmt_fn(abs(d))}</td>'
    return f'<tr><td class="label">{label}</td>{cells}</tr>'

# ─── KPI table data ───────────────────────────────────────────────────────────
rows_kpi = ""
rows_kpi += kpi_row("Blended Revenue",  [TW[w]["blended"] for w in WEEKS], money, "up")
rows_kpi += kpi_row("Total Ad Spend",   [TW[w]["spend"]   for w in WEEKS], money, "down")
rows_kpi += kpi_row("Net Profit",       [TW[w]["profit"]  for w in WEEKS], money, "up")
rows_kpi += kpi_row("Profit Margin",    [TW[w]["margin"]  for w in WEEKS], pct,   "up")
rows_kpi += kpi_row("MER",             [TW[w]["mer"]     for w in WEEKS], pct,   "down")
rows_kpi += kpi_row("Blended ROAS",    [TW[w]["roas"]    for w in WEEKS], lambda v: f"{v:.2f}x", "up")
rows_kpi += kpi_row("NC-ROAS",         [TW[w]["nc_roas"] for w in WEEKS], lambda v: f"{v:.2f}x", "up")
rows_kpi += kpi_row("NCPA",            [TW[w]["ncpa"]    for w in WEEKS], lambda v: f"${v:.0f}",  "down")
rows_kpi += kpi_row("Google Spend",    [TW[w]["google"]  for w in WEEKS], money, "neutral")
rows_kpi += kpi_row("Meta Spend",      [TW[w]["meta"]    for w in WEEKS], money, "down")

# ─── Meta spend table ────────────────────────────────────────────────────────
rows_fb = ""
for cat in fb_weekly.index:
    row = f'<tr><td class="label">{cat}</td>'
    for w in WEEKS:
        v = fb_weekly.loc[cat, w] if w in fb_weekly.columns else 0
        row += f'<td class="num">{money(v)}</td>'
    row += f'<td class="num bold">{money(fb_weekly.loc[cat, "Total"])}</td></tr>'
    rows_fb += row
# Total row
rows_fb += '<tr class="total-row"><td class="label">Total Meta Spend</td>'
for w in WEEKS:
    total = sum(fb_weekly.loc[cat, w] if w in fb_weekly.columns else 0 for cat in fb_weekly.index)
    rows_fb += f'<td class="num">{money(total)}</td>'
rows_fb += f'<td class="num bold">{money(fb_weekly["Total"].sum())}</td></tr>'

# ─── Shopify table ────────────────────────────────────────────────────────────
rows_shop = ""
for prod in top_products.index:
    row = f'<tr><td class="label">{prod}</td>'
    for w in WEEKS:
        v = top_products.loc[prod, w] if w in top_products.columns else 0
        row += f'<td class="num">{money(v)}</td>'
    row += f'<td class="num bold">{money(top_products.loc[prod, "Total"])}</td></tr>'
    rows_shop += row

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LogOX — 4-Week Performance Report | Mar 2–29, 2026</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --green:   {BRAND_GREEN};
    --accent:  {BRAND_ACCENT};
    --bg:      #F8FAF9;
    --card:    #FFFFFF;
    --border:  #E2EDE8;
    --text:    #1A1A1A;
    --muted:   #6B7280;
    --pos:     #16A34A;
    --neg:     #DC2626;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: var(--bg); color: var(--text); font-size: 14px; }}
  header {{ background: var(--green); color: #fff; padding: 28px 40px; }}
  header h1 {{ font-size: 22px; font-weight: 700; letter-spacing: -0.3px; }}
  header p  {{ margin-top: 4px; opacity: 0.8; font-size: 13px; }}
  .badge {{ display: inline-block; background: rgba(255,255,255,0.15);
             border-radius: 4px; padding: 2px 10px; font-size: 12px; margin-top: 8px; }}
  main {{ max-width: 1200px; margin: 32px auto; padding: 0 24px; }}

  /* Section labels */
  .section-title {{ font-size: 16px; font-weight: 700; color: var(--green);
                    margin: 36px 0 14px; border-left: 4px solid var(--accent);
                    padding-left: 10px; }}

  /* KPI scorecards */
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 8px; }}
  .kpi-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px;
               padding: 16px 18px; }}
  .kpi-card .week {{ font-size: 11px; font-weight: 600; color: var(--muted);
                     text-transform: uppercase; letter-spacing: 0.6px; }}
  .kpi-card .revenue {{ font-size: 22px; font-weight: 800; color: var(--green); margin-top: 4px; }}
  .kpi-card .spend   {{ font-size: 13px; color: var(--muted); margin-top: 2px; }}
  .kpi-card .mer     {{ font-size: 13px; font-weight: 700; margin-top: 6px; }}
  .kpi-card .profit  {{ font-size: 13px; margin-top: 2px; }}
  .kpi-card .roas    {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}
  .kpi-card.w1 {{ border-top: 3px solid #1B4332; }}
  .kpi-card.w2 {{ border-top: 3px solid #2D6A4F; }}
  .kpi-card.w3 {{ border-top: 3px solid #52B788; }}
  .kpi-card.w4 {{ border-top: 3px solid #95D5B2; }}

  /* Improvement callout */
  .insight-box {{ background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 10px;
                  padding: 16px 20px; margin-bottom: 12px; }}
  .insight-box h3 {{ font-size: 13px; font-weight: 700; color: #166534; margin-bottom: 8px; }}
  .insight-box ul {{ padding-left: 18px; }}
  .insight-box li {{ font-size: 13px; color: #166534; margin-bottom: 4px; line-height: 1.5; }}

  /* Charts */
  .chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 8px; }}
  .chart-card {{ background: var(--card); border: 1px solid var(--border);
                 border-radius: 10px; padding: 20px; }}
  .chart-card h3 {{ font-size: 13px; font-weight: 700; color: var(--muted);
                    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px; }}
  .chart-full {{ background: var(--card); border: 1px solid var(--border);
                 border-radius: 10px; padding: 20px; margin-bottom: 8px; }}
  .chart-full h3 {{ font-size: 13px; font-weight: 700; color: var(--muted);
                    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px; }}

  /* Tables */
  .table-card {{ background: var(--card); border: 1px solid var(--border);
                 border-radius: 10px; overflow: hidden; margin-bottom: 24px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead {{ background: var(--green); color: #fff; }}
  thead th {{ padding: 10px 14px; font-size: 12px; font-weight: 600;
              text-align: left; letter-spacing: 0.3px; }}
  thead th.num {{ text-align: right; }}
  tbody tr {{ border-bottom: 1px solid var(--border); }}
  tbody tr:last-child {{ border-bottom: none; }}
  tbody tr:hover {{ background: #F0FDF4; }}
  td {{ padding: 9px 14px; font-size: 13px; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  td.label {{ font-weight: 500; }}
  td.bold {{ font-weight: 700; }}
  td.delta {{ font-weight: 700; font-size: 12px; }}
  td.pos {{ color: var(--pos); }}
  td.neg {{ color: var(--neg); }}
  tr.total-row {{ background: #F0FDF4; font-weight: 700; }}
  tr.total-row td {{ font-weight: 700; }}

  /* Channel split pills */
  .channel-row {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
  .pill {{ border-radius: 20px; padding: 6px 14px; font-size: 12px; font-weight: 600; color: #fff; }}

  footer {{ text-align: center; color: var(--muted); font-size: 12px;
            margin: 40px 0 24px; }}
</style>
</head>
<body>

<header>
  <h1>LogOX — 4-Week Performance Report</h1>
  <p>March 2–29, 2026 &nbsp;|&nbsp; Prepared by Interconnections</p>
  <span class="badge">Triple Whale Attribution + Shopify + Meta Ads</span>
</header>

<main>

<!-- ── WEEK SCORECARDS ─────────────────────────────────────────────────────── -->
<div class="section-title">Weekly Snapshot</div>
<div class="kpi-grid">
{''.join([f'''
  <div class="kpi-card w{i+1}">
    <div class="week">{TW[w]["label"]}</div>
    <div class="revenue">{money(TW[w]["blended"])}</div>
    <div class="spend">Ad Spend: {money(TW[w]["spend"])}</div>
    <div class="mer" style="color:{'var(--pos)' if TW[w]['mer'] <= 0.24 else 'var(--neg)'}">MER: {pct(TW[w]['mer'])}</div>
    <div class="profit">Profit: {money(TW[w]["profit"])} ({pct(TW[w]["margin"])})</div>
    <div class="roas">ROAS {TW[w]["roas"]:.2f}x &nbsp;|&nbsp; NC-ROAS {TW[w]["nc_roas"]:.2f}x &nbsp;|&nbsp; NCPA ${TW[w]["ncpa"]:.0f}</div>
  </div>''' for i, w in enumerate(WEEKS)])}
</div>

<!-- ── KEY WINS ─────────────────────────────────────────────────────────────── -->
<div class="section-title">Key Wins</div>
<div class="insight-box">
  <h3>What improved over the 4 weeks</h3>
  <ul>
    <li><strong>MER improved from 33% → 22%</strong> by W3 — spending less for every dollar of revenue driven.</li>
    <li><strong>Ad spend cut 29%</strong> (W1 $10,028 → W4 $7,726) while blended revenue stayed in the $35–$41K range.</li>
    <li><strong>Net profit nearly tripled</strong>: W1 $3,960 (13% margin) → W4 $9,400 (29% margin).</li>
    <li><strong>ROAS improved 37%</strong>: 3.04x → 4.18x; NC-ROAS improved 30%: 2.98x → 3.88x.</li>
    <li><strong>NCPA dropped 40%</strong>: $120.80 → $72.90 — new customers cost far less to acquire by W4.</li>
    <li><strong>Google Ads budget scaled 154%</strong> (W1 $963 → W4 $2,444) as Meta was scaled back — a cleaner, higher-intent channel mix.</li>
  </ul>
</div>

<!-- ── CHANNEL MIX CHARTS ─────────────────────────────────────────────────── -->
<div class="section-title">Channel Mix &amp; Efficiency Trends</div>
<div class="chart-grid">
  <div class="chart-card">
    <h3>Ad Spend by Channel (Weekly)</h3>
    <canvas id="channelChart" height="220"></canvas>
  </div>
  <div class="chart-card">
    <h3>MER &amp; ROAS Week-over-Week</h3>
    <canvas id="efficiencyChart" height="220"></canvas>
  </div>
</div>

<div class="chart-grid">
  <div class="chart-card">
    <h3>Net Profit by Week ($)</h3>
    <canvas id="profitChart" height="220"></canvas>
  </div>
  <div class="chart-card">
    <h3>NCPA by Week ($) — Lower is Better</h3>
    <canvas id="ncpaChart" height="220"></canvas>
  </div>
</div>

<!-- ── META SPEND BY PRODUCT ─────────────────────────────────────────────── -->
<div class="section-title">Meta Spend by Product Category</div>
<div class="chart-full">
  <h3>Meta Ad Spend by Product — Weekly Breakdown ($)</h3>
  <canvas id="fbProductChart" height="160"></canvas>
</div>

<div class="table-card">
  <table>
    <thead>
      <tr>
        <th>Product Category</th>
        <th class="num">W1 (Mar 2–8)</th>
        <th class="num">W2 (Mar 9–15)</th>
        <th class="num">W3 (Mar 16–22)</th>
        <th class="num">W4 (Mar 23–29)</th>
        <th class="num">4-Week Total</th>
      </tr>
    </thead>
    <tbody>{rows_fb}</tbody>
  </table>
</div>

<!-- ── SHOPIFY REVENUE BY PRODUCT ─────────────────────────────────────────── -->
<div class="section-title">Shopify Revenue by Product</div>
<div class="chart-full">
  <h3>Shopify Net Sales by Product — Weekly ($)</h3>
  <canvas id="shopProductChart" height="160"></canvas>
</div>

<div class="table-card">
  <table>
    <thead>
      <tr>
        <th>Product</th>
        <th class="num">W1 (Mar 2–8)</th>
        <th class="num">W2 (Mar 9–15)</th>
        <th class="num">W3 (Mar 16–22)</th>
        <th class="num">W4 (Mar 23–29)</th>
        <th class="num">4-Week Total</th>
      </tr>
    </thead>
    <tbody>{rows_shop}</tbody>
  </table>
</div>

<!-- ── FULL KPI TABLE ─────────────────────────────────────────────────────── -->
<div class="section-title">Full KPI Summary (Triple Whale)</div>
<div class="table-card">
  <table>
    <thead>
      <tr>
        <th>Metric</th>
        <th class="num">W1 (Mar 2–8)</th>
        <th class="num">W2 (Mar 9–15)</th>
        <th class="num">W3 (Mar 16–22)</th>
        <th class="num">W4 (Mar 23–29)</th>
        <th class="num">W1→W4 Change</th>
      </tr>
    </thead>
    <tbody>{rows_kpi}</tbody>
  </table>
</div>

</main>

<footer>
  Interconnections &nbsp;|&nbsp; Generated {datetime.now().strftime("%B %d, %Y")} &nbsp;|&nbsp; Data: Triple Whale + Shopify + Meta Ads Manager
</footer>

<script>
const labels = {labels_js};
const wColors = {json.dumps(WEEK_COLORS)};

// Channel spend chart (stacked bar)
new Chart(document.getElementById('channelChart'), {{
  type: 'bar',
  data: {{
    labels,
    datasets: [
      {{ label: 'Google', data: {google_vals}, backgroundColor: '{GOOGLE_BLUE}', borderRadius: 3 }},
      {{ label: 'Meta',   data: {meta_vals},   backgroundColor: '{META_BLUE}',   borderRadius: 3 }},
      {{ label: 'Microsoft', data: {ms_vals},  backgroundColor: '{MS_GRAY}',     borderRadius: 3 }},
    ]
  }},
  options: {{
    plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 11 }} }} }} }},
    scales: {{
      x: {{ stacked: true, grid: {{ display: false }} }},
      y: {{ stacked: true, ticks: {{ callback: v => '$' + v.toLocaleString() }}, grid: {{ color: '#F0F0F0' }} }}
    }},
    responsive: true
  }}
}});

// MER & ROAS dual axis
new Chart(document.getElementById('efficiencyChart'), {{
  type: 'line',
  data: {{
    labels,
    datasets: [
      {{ label: 'MER (%)', data: {mer_vals}, borderColor: '#DC2626', backgroundColor: 'rgba(220,38,38,0.1)',
        tension: 0.3, fill: true, yAxisID: 'yL', pointRadius: 5, pointBackgroundColor: '#DC2626' }},
      {{ label: 'ROAS (x)', data: {roas_vals}, borderColor: '{BRAND_GREEN}', backgroundColor: 'rgba(45,106,79,0.08)',
        tension: 0.3, fill: true, yAxisID: 'yR', pointRadius: 5, pointBackgroundColor: '{BRAND_GREEN}' }},
      {{ label: 'NC-ROAS (x)', data: {nc_roas_vals}, borderColor: '{BRAND_ACCENT}', borderDash: [4,4],
        tension: 0.3, yAxisID: 'yR', pointRadius: 5, pointBackgroundColor: '{BRAND_ACCENT}' }},
    ]
  }},
  options: {{
    plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 11 }} }} }} }},
    scales: {{
      yL: {{ type: 'linear', position: 'left',  ticks: {{ callback: v => v + '%' }}, grid: {{ color: '#F0F0F0' }} }},
      yR: {{ type: 'linear', position: 'right', ticks: {{ callback: v => v + 'x' }}, grid: {{ display: false }} }},
      x: {{ grid: {{ display: false }} }}
    }},
    responsive: true
  }}
}});

// Profit chart
new Chart(document.getElementById('profitChart'), {{
  type: 'bar',
  data: {{
    labels,
    datasets: [{{ label: 'Net Profit ($)', data: {profit_vals},
      backgroundColor: wColors, borderRadius: 4 }}]
  }},
  options: {{
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ grid: {{ display: false }} }},
      y: {{ ticks: {{ callback: v => '$' + v.toLocaleString() }}, grid: {{ color: '#F0F0F0' }} }}
    }},
    responsive: true
  }}
}});

// NCPA chart
new Chart(document.getElementById('ncpaChart'), {{
  type: 'bar',
  data: {{
    labels,
    datasets: [{{ label: 'NCPA ($)', data: {ncpa_vals},
      backgroundColor: ['#DC2626','#F59E0B','#52B788','#2D6A4F'], borderRadius: 4 }}]
  }},
  options: {{
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ grid: {{ display: false }} }},
      y: {{ ticks: {{ callback: v => '$' + v }}, grid: {{ color: '#F0F0F0' }} }}
    }},
    responsive: true
  }}
}});

// Meta spend by product (stacked)
new Chart(document.getElementById('fbProductChart'), {{
  type: 'bar',
  data: {{ labels, datasets: {fb_chart_js} }},
  options: {{
    plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 11 }}, boxWidth: 12 }} }} }},
    scales: {{
      x: {{ stacked: true, grid: {{ display: false }} }},
      y: {{ stacked: true, ticks: {{ callback: v => '$' + v.toLocaleString() }}, grid: {{ color: '#F0F0F0' }} }}
    }},
    responsive: true
  }}
}});

// Shopify product revenue (stacked)
new Chart(document.getElementById('shopProductChart'), {{
  type: 'bar',
  data: {{ labels, datasets: {shop_chart_js} }},
  options: {{
    plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 11 }}, boxWidth: 12 }} }} }},
    scales: {{
      x: {{ stacked: true, grid: {{ display: false }} }},
      y: {{ stacked: true, ticks: {{ callback: v => '$' + v.toLocaleString() }}, grid: {{ color: '#F0F0F0' }} }}
    }},
    responsive: true
  }}
}});
</script>
</body>
</html>"""

# ─── Write output ─────────────────────────────────────────────────────────────
with open(OUTPUT, "w") as f:
    f.write(HTML)

print(f"✓ Report written to:\n  {OUTPUT}")
