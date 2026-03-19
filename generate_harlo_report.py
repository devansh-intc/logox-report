#!/usr/bin/env python3
"""
Harlo Amazon Ads Audit Report Generator
Reads all CSV files and produces a comprehensive HTML audit report.
"""

import csv
import os
from datetime import datetime

DATA_DIR = "/Users/devan/Downloads/Harlo Amz"
OUTPUT_DIR = "/Users/devan/Desktop/Claude Code Agents/Shopify Product Data Analysis/reports"

def read_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    rows = []
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def parse_money(val):
    if not val:
        return 0.0
    val = str(val).replace('US$', '').replace('$', '').replace(',', '').replace('"', '').strip()
    try:
        return float(val)
    except:
        return 0.0

def parse_pct(val):
    if not val:
        return 0.0
    val = str(val).replace('%', '').replace('"', '').strip()
    try:
        return float(val)
    except:
        return 0.0

def parse_float(val):
    if not val:
        return 0.0
    val = str(val).replace(',', '').replace('"', '').strip()
    try:
        return float(val)
    except:
        return 0.0

def parse_int(val):
    if not val:
        return 0
    val = str(val).replace(',', '').replace('"', '').strip()
    try:
        return int(float(val))
    except:
        return 0

def main():
    # === LOAD DATA ===
    # Doc 1: All campaign types (SP, SB, SD) from Amazon Campaign dashboard
    all_campaigns = read_csv("Amazon Campaign_Feb 1st to Mar_19_2026.csv")

    # Doc 2: Advertised product report
    adv_products = read_csv("Sponsored_Products_Advertised_product_report.csv")

    # Doc 3: SP Campaign report
    sp_campaigns = read_csv("Sponsored_Products_Campaign_report.csv")

    # Doc 5: Placement report
    placements = read_csv("Sponsored_Products_Placement_report.csv")

    # Doc 6: Search term report
    search_terms = read_csv("Sponsored_Products_Search_term_report.csv")

    # Doc 7: Targeting report (SP)
    targeting = read_csv("Sponsored_Products_Targeting_report.csv")

    # Doc 8: Targeting with bids
    targeting_bids = read_csv("Targeting_Feb 1 till Mar_19_2026.csv")

    # Doc 9: Business Report
    business_report = read_csv("BusinessReport-1 Feb till 9th March 2026.csv")

    # === PROCESS ALL CAMPAIGNS (Doc 1) ===
    campaign_data = []
    for row in all_campaigns:
        name = row.get('Campaign name', '')
        ctype = row.get('Type', '')
        spend = parse_money(row.get('Total cost (converted)', row.get('Total cost', 0)))
        sales = parse_money(row.get('Sales (converted)', row.get('Sales', 0)))
        purchases = parse_int(row.get('Purchases', 0))
        impressions = parse_int(row.get('Impressions', 0))
        clicks = parse_int(row.get('Clicks', 0))
        state = row.get('State', row.get('Status', ''))
        portfolio = row.get('Portfolio name', '')
        targeting_type = row.get('Targeting', '')
        bid_strategy = row.get('Campaign bid strategy', '')

        acos = (spend / sales * 100) if sales > 0 else None
        roas = (sales / spend) if spend > 0 else None

        campaign_data.append({
            'name': name,
            'type': ctype,
            'spend': spend,
            'sales': sales,
            'purchases': purchases,
            'impressions': impressions,
            'clicks': clicks,
            'state': state,
            'portfolio': portfolio,
            'targeting': targeting_type,
            'bid_strategy': bid_strategy,
            'acos': acos,
            'roas': roas
        })

    # Filter to campaigns with spend > 0
    active_campaigns = [c for c in campaign_data if c['spend'] > 0]
    active_campaigns.sort(key=lambda x: x['spend'], reverse=True)

    total_spend = sum(c['spend'] for c in active_campaigns)
    total_sales = sum(c['sales'] for c in active_campaigns)
    total_purchases = sum(c['purchases'] for c in active_campaigns)
    total_clicks = sum(c['clicks'] for c in active_campaigns)
    total_impressions = sum(c['impressions'] for c in active_campaigns)
    overall_acos = (total_spend / total_sales * 100) if total_sales > 0 else 0
    overall_roas = (total_sales / total_spend) if total_spend > 0 else 0
    overall_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
    overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    overall_cvr = (total_purchases / total_clicks * 100) if total_clicks > 0 else 0

    # By campaign type
    sp_total_spend = sum(c['spend'] for c in active_campaigns if c['type'] == 'SP')
    sp_total_sales = sum(c['sales'] for c in active_campaigns if c['type'] == 'SP')
    sb_total_spend = sum(c['spend'] for c in active_campaigns if c['type'] == 'SB2')
    sb_total_sales = sum(c['sales'] for c in active_campaigns if c['type'] == 'SB2')
    sd_total_spend = sum(c['spend'] for c in active_campaigns if c['type'] == 'SD')
    sd_total_sales = sum(c['sales'] for c in active_campaigns if c['type'] == 'SD')

    # Branded vs Non-Branded
    branded_campaigns = [c for c in active_campaigns if 'branded' in c['name'].lower() or 'brand' in c['name'].lower()]
    nonbranded_campaigns = [c for c in active_campaigns if 'branded' not in c['name'].lower() and 'brand' not in c['name'].lower()]

    branded_spend = sum(c['spend'] for c in branded_campaigns)
    branded_sales = sum(c['sales'] for c in branded_campaigns)
    nonbranded_spend = sum(c['spend'] for c in nonbranded_campaigns)
    nonbranded_sales = sum(c['sales'] for c in nonbranded_campaigns)

    # === PROCESS SP CAMPAIGNS (Doc 3) ===
    sp_camp_detail = []
    for row in sp_campaigns:
        name = row.get('Campaign Name', '')
        spend = parse_money(row.get('Spend', 0))
        sales = parse_money(row.get('7 Day Total Sales', 0))
        orders = parse_int(row.get('7 Day Total Orders (#)', 0))
        impressions = parse_int(row.get('Impressions', 0))
        clicks = parse_int(row.get('Clicks', 0))
        budget = row.get('Budget', '')
        targeting_type = row.get('Targeting Type', '')
        bid_strategy = row.get('Bidding strategy', '')
        portfolio = row.get('Portfolio name', '')
        status = row.get('Status', '')

        ly_spend = parse_money(row.get('Last Year Spend', 0))
        ly_clicks = parse_int(row.get('Last Year Clicks', 0))
        ly_impressions = parse_int(row.get('Last Year Impressions', 0))

        acos = (spend / sales * 100) if sales > 0 else None
        roas = (sales / spend) if spend > 0 else None
        cpc = (spend / clicks) if clicks > 0 else 0

        sp_camp_detail.append({
            'name': name,
            'spend': spend,
            'sales': sales,
            'orders': orders,
            'impressions': impressions,
            'clicks': clicks,
            'budget': budget,
            'targeting': targeting_type,
            'bid_strategy': bid_strategy,
            'portfolio': portfolio,
            'status': status,
            'acos': acos,
            'roas': roas,
            'cpc': cpc,
            'ly_spend': ly_spend,
            'ly_clicks': ly_clicks,
            'ly_impressions': ly_impressions
        })

    sp_camp_detail.sort(key=lambda x: x['spend'], reverse=True)

    # === PROCESS TARGETING WITH BIDS (Doc 8) ===
    bid_data = []
    for row in targeting_bids:
        target = row.get('Target', '')
        target_type = row.get('Targeting type', '')
        campaign = row.get('Campaign', '')
        bid = parse_float(row.get('Bid', 0))
        suggested = parse_float(row.get('Suggested bid', 0))
        spend = parse_float(row.get('Spend', 0))
        sales = parse_float(row.get('Sales', 0))
        roas_val = parse_float(row.get('ROAS', 0))
        acos_val = parse_float(row.get('ACOS', 0))
        impressions = parse_int(row.get('Impressions', 0))
        clicks = parse_int(row.get('Clicks', 0))
        orders = parse_int(row.get('Orders', 0))
        cvr = parse_float(row.get('Conversion rate', 0))
        tos_is = row.get('Top-of-search IS', '')
        cpc_val = parse_float(row.get('CPC', 0))

        bid_data.append({
            'target': target,
            'target_type': target_type,
            'campaign': campaign,
            'bid': bid,
            'suggested': suggested,
            'spend': spend,
            'sales': sales,
            'roas': roas_val,
            'acos': acos_val * 100 if acos_val < 10 else acos_val,  # normalize
            'impressions': impressions,
            'clicks': clicks,
            'orders': orders,
            'cvr': cvr * 100 if cvr < 1 else cvr,
            'tos_is': tos_is,
            'cpc': cpc_val
        })

    bid_data.sort(key=lambda x: x['spend'], reverse=True)

    # === PROCESS PLACEMENTS (Doc 5) ===
    # Aggregate by campaign + placement
    placement_agg = {}
    for row in placements:
        campaign = row.get('Campaign Name', '')
        placement = row.get('Placement', '')
        spend = parse_money(row.get('Spend', 0))
        sales = parse_money(row.get('7 Day Total Sales', 0))
        clicks = parse_int(row.get('Clicks', 0))
        impressions = parse_int(row.get('Impressions', 0))
        orders = parse_int(row.get('7 Day Total Orders (#)', 0))

        key = (campaign, placement)
        if key not in placement_agg:
            placement_agg[key] = {'spend': 0, 'sales': 0, 'clicks': 0, 'impressions': 0, 'orders': 0}
        placement_agg[key]['spend'] += spend
        placement_agg[key]['sales'] += sales
        placement_agg[key]['clicks'] += clicks
        placement_agg[key]['impressions'] += impressions
        placement_agg[key]['orders'] += orders

    # Aggregate by placement type only
    placement_totals = {}
    for (camp, place), data in placement_agg.items():
        if place not in placement_totals:
            placement_totals[place] = {'spend': 0, 'sales': 0, 'clicks': 0, 'impressions': 0, 'orders': 0}
        placement_totals[place]['spend'] += data['spend']
        placement_totals[place]['sales'] += data['sales']
        placement_totals[place]['clicks'] += data['clicks']
        placement_totals[place]['impressions'] += data['impressions']
        placement_totals[place]['orders'] += data['orders']

    # === PROCESS SEARCH TERMS (Doc 6) ===
    # Find high-spend zero-sale terms
    search_term_data = []
    for row in search_terms:
        term = row.get('Customer Search Term', '')
        spend = parse_money(row.get('Spend', 0))
        sales = parse_money(row.get('7 Day Total Sales', 0))
        clicks = parse_int(row.get('Clicks', 0))
        impressions = parse_int(row.get('Impressions', 0))
        orders = parse_int(row.get('7 Day Total Orders (#)', 0))
        campaign = row.get('Campaign Name', '')
        match_type = row.get('Match Type', '')
        targeting = row.get('Targeting', '')

        search_term_data.append({
            'term': term,
            'spend': spend,
            'sales': sales,
            'clicks': clicks,
            'impressions': impressions,
            'orders': orders,
            'campaign': campaign,
            'match_type': match_type,
            'targeting': targeting
        })

    # Aggregate search terms
    term_agg = {}
    for st in search_term_data:
        t = st['term']
        if t not in term_agg:
            term_agg[t] = {'spend': 0, 'sales': 0, 'clicks': 0, 'orders': 0, 'impressions': 0}
        term_agg[t]['spend'] += st['spend']
        term_agg[t]['sales'] += st['sales']
        term_agg[t]['clicks'] += st['clicks']
        term_agg[t]['orders'] += st['orders']
        term_agg[t]['impressions'] += st['impressions']

    # Negate candidates: spend > $3, 0 sales, clicks >= 2
    negate_candidates = []
    for term, data in term_agg.items():
        if data['spend'] >= 3 and data['orders'] == 0 and data['clicks'] >= 2:
            negate_candidates.append({'term': term, **data})
    negate_candidates.sort(key=lambda x: x['spend'], reverse=True)

    # Winner search terms: orders > 0, ACOS < 40% (under breakeven = profitable)
    winner_terms = []
    for term, data in term_agg.items():
        if data['orders'] > 0 and data['sales'] > 0:
            acos = data['spend'] / data['sales'] * 100
            if acos < 40:
                winner_terms.append({'term': term, 'acos': acos, **data})
    winner_terms.sort(key=lambda x: x['sales'], reverse=True)

    # === PROCESS ADVERTISED PRODUCTS (Doc 2) ===
    product_agg = {}
    for row in adv_products:
        sku = row.get('Advertised SKU', '')
        asin = row.get('Advertised ASIN', '')
        spend = parse_money(row.get('Spend', 0))
        sales = parse_money(row.get('7 Day Total Sales', 0))
        orders = parse_int(row.get('7 Day Total Orders (#)', 0))
        clicks = parse_int(row.get('Clicks', 0))
        impressions = parse_int(row.get('Impressions', 0))
        adv_sales = parse_money(row.get('7 Day Advertised SKU Sales', 0))
        other_sales = parse_money(row.get('7 Day Other SKU Sales', 0))

        key = (sku, asin)
        if key not in product_agg:
            product_agg[key] = {'spend': 0, 'sales': 0, 'orders': 0, 'clicks': 0, 'impressions': 0, 'adv_sales': 0, 'other_sales': 0}
        product_agg[key]['spend'] += spend
        product_agg[key]['sales'] += sales
        product_agg[key]['orders'] += orders
        product_agg[key]['clicks'] += clicks
        product_agg[key]['impressions'] += impressions
        product_agg[key]['adv_sales'] += adv_sales
        product_agg[key]['other_sales'] += other_sales

    product_list = []
    for (sku, asin), data in product_agg.items():
        acos = (data['spend'] / data['sales'] * 100) if data['sales'] > 0 else None
        roas = (data['sales'] / data['spend']) if data['spend'] > 0 else None
        product_list.append({'sku': sku, 'asin': asin, 'acos': acos, 'roas': roas, **data})
    product_list.sort(key=lambda x: x['spend'], reverse=True)

    # === PROCESS BUSINESS REPORT (Doc 9) ===
    biz_data = []
    for row in business_report:
        date = row.get('Date', '')
        sales = parse_money(row.get('Ordered Product Sales', 0))
        units = parse_int(row.get('Units Ordered', 0))
        sessions = parse_int(row.get('Sessions - Total', 0))
        page_views = parse_int(row.get('Page Views - Total', 0))
        buy_box = parse_pct(row.get('Featured Offer (Buy Box) Percentage', '0'))
        cvr = parse_pct(row.get('Unit Session Percentage', '0'))

        biz_data.append({
            'date': date,
            'sales': sales,
            'units': units,
            'sessions': sessions,
            'page_views': page_views,
            'buy_box': buy_box,
            'cvr': cvr
        })

    biz_total_sales = sum(b['sales'] for b in biz_data)
    biz_total_units = sum(b['units'] for b in biz_data)
    biz_total_sessions = sum(b['sessions'] for b in biz_data)
    biz_avg_buy_box = sum(b['buy_box'] for b in biz_data) / len(biz_data) if biz_data else 0
    biz_avg_cvr = sum(b['cvr'] for b in biz_data) / len(biz_data) if biz_data else 0

    # Buy box trend
    feb_bb = [b for b in biz_data if b['date'].startswith('2/')]
    mar_bb = [b for b in biz_data if b['date'].startswith('3/')]
    feb_avg_bb = sum(b['buy_box'] for b in feb_bb) / len(feb_bb) if feb_bb else 0
    mar_avg_bb = sum(b['buy_box'] for b in mar_bb) / len(mar_bb) if mar_bb else 0

    # Count campaigns
    total_campaigns = len(campaign_data)
    enabled_campaigns = len([c for c in campaign_data if 'ENABLED' in c['state'].upper()])
    paused_campaigns = len([c for c in campaign_data if 'PAUSED' in c['state'].upper()])
    zero_spend_campaigns = len([c for c in campaign_data if c['spend'] == 0])

    # Perpetua campaigns
    perpetua_campaigns = [c for c in active_campaigns if 'perpetua' in c['name'].lower()]
    perpetua_spend = sum(c['spend'] for c in perpetua_campaigns)
    perpetua_sales = sum(c['sales'] for c in perpetua_campaigns)

    # === BUILD HTML ===

    def fmt_money(v):
        return f"${v:,.2f}"

    def fmt_pct(v):
        return f"{v:.1f}%"

    def fmt_num(v):
        return f"{v:,}"

    def acos_color(acos):
        """40% = breakeven. Below 40% = profitable, above 40% = loss."""
        if acos is None:
            return '#6C6C6C'
        if acos <= 20:
            return '#5F9598'  # primary teal — excellent
        elif acos <= 40:
            return '#1e2328'  # dark — profitable, under breakeven
        else:
            return '#1e2328'  # dark with bold — above breakeven (loss)

    def acos_tag(acos):
        """Returns a styled tag for ACOS values."""
        if acos is None:
            return '<span style="color:#6C6C6C">—</span>'
        if acos <= 20:
            return f'<span style="color:#5F9598;font-weight:700">{fmt_pct(acos)}</span>'
        elif acos <= 40:
            return f'<span style="color:#5F9598;font-weight:600">{fmt_pct(acos)}</span>'
        else:
            return f'<span style="font-weight:700;background:#1e2328;color:#fff;padding:2px 6px;border-radius:3px">{fmt_pct(acos)}</span>'

    def roas_color(roas):
        """2.5x ROAS = 40% ACOS breakeven."""
        if roas is None:
            return '#6C6C6C'
        if roas >= 5:
            return '#5F9598'  # excellent
        elif roas >= 2.5:
            return '#5F9598'  # profitable
        else:
            return '#1e2328'  # below breakeven

    # Top 15 campaigns by spend
    top_camps_html = ""
    for c in active_campaigns[:20]:
        acos_str = fmt_pct(c['acos']) if c['acos'] is not None else '—'
        roas_str = f"{c['roas']:.2f}" if c['roas'] is not None else '—'
        ac = acos_color(c['acos'])
        rc = roas_color(c['roas'])
        name_short = c['name'][:65] + ('...' if len(c['name']) > 65 else '')
        top_camps_html += f"""<tr>
            <td style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:380px;" title="{c['name']}">{name_short}</td>
            <td>{c['type']}</td>
            <td>{c['portfolio'] or '—'}</td>
            <td style="text-align:right">{fmt_money(c['spend'])}</td>
            <td style="text-align:right">{fmt_money(c['sales'])}</td>
            <td style="text-align:right;color:{ac};font-weight:600">{acos_str}</td>
            <td style="text-align:right;color:{rc};font-weight:600">{roas_str}</td>
            <td style="text-align:right">{c['purchases']}</td>
        </tr>"""

    # Best branded campaigns
    branded_html = ""
    branded_sorted = sorted(branded_campaigns, key=lambda x: x['sales'], reverse=True)
    for c in branded_sorted[:10]:
        if c['spend'] == 0:
            continue
        acos_str = fmt_pct(c['acos']) if c['acos'] is not None else '—'
        roas_str = f"{c['roas']:.2f}" if c['roas'] is not None else '—'
        ac = acos_color(c['acos'])
        name_short = c['name'][:60] + ('...' if len(c['name']) > 60 else '')
        branded_html += f"""<tr>
            <td title="{c['name']}">{name_short}</td>
            <td style="text-align:right">{fmt_money(c['spend'])}</td>
            <td style="text-align:right">{fmt_money(c['sales'])}</td>
            <td style="text-align:right;color:{ac};font-weight:600">{acos_str}</td>
            <td style="text-align:right">{c['purchases']}</td>
        </tr>"""

    # Worst performing (high spend, bad ACOS)
    worst_camps = [c for c in active_campaigns if c['spend'] >= 10 and (c['acos'] is None or c['acos'] > 50)]
    worst_camps.sort(key=lambda x: x['spend'], reverse=True)
    worst_html = ""
    for c in worst_camps[:15]:
        acos_str = fmt_pct(c['acos']) if c['acos'] is not None else 'No Sales'
        name_short = c['name'][:60] + ('...' if len(c['name']) > 60 else '')
        worst_html += f"""<tr>
            <td title="{c['name']}">{name_short}</td>
            <td>{c['type']}</td>
            <td style="text-align:right">{fmt_money(c['spend'])}</td>
            <td style="text-align:right">{fmt_money(c['sales'])}</td>
            <td style="text-align:right"><span style="font-weight:700;background:#1e2328;color:#fff;padding:2px 6px;border-radius:3px">{acos_str}</span></td>
            <td style="text-align:right">{c['clicks']}</td>
        </tr>"""

    # Product performance
    product_html = ""
    for p in product_list:
        if p['spend'] < 1:
            continue
        acos_str = fmt_pct(p['acos']) if p['acos'] is not None else '—'
        roas_str = f"{p['roas']:.2f}" if p['roas'] is not None else '—'
        ac = acos_color(p['acos'])
        product_html += f"""<tr>
            <td>{p['sku']}</td>
            <td style="font-family:monospace;font-size:0.8em">{p['asin']}</td>
            <td style="text-align:right">{fmt_money(p['spend'])}</td>
            <td style="text-align:right">{fmt_money(p['sales'])}</td>
            <td style="text-align:right;color:{ac};font-weight:600">{acos_str}</td>
            <td style="text-align:right">{p['orders']}</td>
            <td style="text-align:right">{fmt_money(p['adv_sales'])}</td>
            <td style="text-align:right">{fmt_money(p['other_sales'])}</td>
        </tr>"""

    # Placement performance
    placement_html = ""
    for place, data in sorted(placement_totals.items(), key=lambda x: x[1]['spend'], reverse=True):
        if data['spend'] == 0:
            continue
        acos = (data['spend'] / data['sales'] * 100) if data['sales'] > 0 else None
        roas = (data['sales'] / data['spend']) if data['spend'] > 0 else None
        acos_str = fmt_pct(acos) if acos is not None else '—'
        roas_str = f"{roas:.2f}" if roas is not None else '—'
        ac = acos_color(acos)
        placement_html += f"""<tr>
            <td>{place}</td>
            <td style="text-align:right">{fmt_money(data['spend'])}</td>
            <td style="text-align:right">{fmt_money(data['sales'])}</td>
            <td style="text-align:right;color:{ac};font-weight:600">{acos_str}</td>
            <td style="text-align:right">{roas_str}</td>
            <td style="text-align:right">{fmt_num(data['clicks'])}</td>
            <td style="text-align:right">{fmt_num(data['orders'])}</td>
        </tr>"""

    # Bid optimization table (top 25 by spend)
    bid_html = ""
    for b in bid_data[:30]:
        if b['spend'] < 5:
            continue
        acos_val = (b['spend'] / b['sales'] * 100) if b['sales'] > 0 else None
        roas_val = (b['sales'] / b['spend']) if b['spend'] > 0 else None
        acos_str = fmt_pct(acos_val) if acos_val is not None else '—'
        roas_str = f"{roas_val:.2f}" if roas_val is not None else '—'
        ac = acos_color(acos_val)

        # Recommendation (40% ACOS = 2.5x ROAS breakeven)
        if roas_val is not None and roas_val >= 4:
            rec = '<span style="color:#5F9598;font-weight:600">&#9650; Increase</span>'
        elif roas_val is not None and roas_val >= 2.5:
            rec = '<span style="color:#5F9598;font-weight:600">&#9644; Maintain</span>'
        elif roas_val is not None and roas_val > 0 and roas_val < 1.5:
            rec = '<span style="background:#1e2328;color:#fff;padding:2px 6px;border-radius:3px;font-weight:600">&#9660; Decrease / Pause</span>'
        elif acos_val is None or acos_val > 80:
            rec = '<span style="background:#1e2328;color:#fff;padding:2px 6px;border-radius:3px;font-weight:600">&#9660; Decrease / Pause</span>'
        else:
            rec = '<span style="color:#1e2328;font-weight:600">&#9660; Decrease</span>'

        target_short = b['target'][:40] + ('...' if len(b['target']) > 40 else '')
        camp_short = b['campaign'][:35] + ('...' if len(b['campaign']) > 35 else '')

        bid_html += f"""<tr>
            <td title="{b['target']}">{target_short}</td>
            <td style="font-size:0.8em" title="{b['campaign']}">{camp_short}</td>
            <td style="text-align:right">${b['bid']:.2f}</td>
            <td style="text-align:right">${b['suggested']:.2f}</td>
            <td style="text-align:right">{fmt_money(b['spend'])}</td>
            <td style="text-align:right">{fmt_money(b['sales'])}</td>
            <td style="text-align:right;color:{ac};font-weight:600">{acos_str}</td>
            <td style="text-align:center">{rec}</td>
        </tr>"""

    # Negate candidates
    negate_html = ""
    for n in negate_candidates[:25]:
        negate_html += f"""<tr>
            <td>{n['term']}</td>
            <td style="text-align:right">{fmt_money(n['spend'])}</td>
            <td style="text-align:right">{n['clicks']}</td>
            <td style="text-align:right">{fmt_num(n['impressions'])}</td>
        </tr>"""

    # Winner terms
    winner_html = ""
    for w in winner_terms[:20]:
        winner_html += f"""<tr>
            <td>{w['term']}</td>
            <td style="text-align:right">{fmt_money(w['sales'])}</td>
            <td style="text-align:right">{fmt_money(w['spend'])}</td>
            <td style="text-align:right;color:{acos_color(w['acos'])};font-weight:600">{fmt_pct(w['acos'])}</td>
            <td style="text-align:right">{w['orders']}</td>
        </tr>"""

    # Business report
    biz_html = ""
    for b in biz_data:
        bb_color = '#1e2328' if b['buy_box'] < 95 else ('#6C6C6C' if b['buy_box'] < 99 else '#5F9598')
        biz_html += f"""<tr>
            <td>{b['date']}</td>
            <td style="text-align:right">{fmt_money(b['sales'])}</td>
            <td style="text-align:right">{b['units']}</td>
            <td style="text-align:right">{b['sessions']}</td>
            <td style="text-align:right;color:{bb_color};font-weight:600">{fmt_pct(b['buy_box'])}</td>
            <td style="text-align:right">{fmt_pct(b['cvr'])}</td>
        </tr>"""

    # Perpetua assessment
    perpetua_html = ""
    for c in perpetua_campaigns:
        acos_str = fmt_pct(c['acos']) if c['acos'] is not None else '—'
        roas_str = f"{c['roas']:.2f}" if c['roas'] is not None else '—'
        name_short = c['name'][:55] + ('...' if len(c['name']) > 55 else '')
        perpetua_html += f"""<tr>
            <td title="{c['name']}">{name_short}</td>
            <td style="text-align:right">{fmt_money(c['spend'])}</td>
            <td style="text-align:right">{fmt_money(c['sales'])}</td>
            <td style="text-align:right">{fmt_num(c['impressions'])}</td>
            <td style="text-align:right">{c['clicks']}</td>
            <td style="text-align:right">{c['purchases']}</td>
        </tr>"""

    # Campaign count by portfolio
    portfolio_counts = {}
    for c in campaign_data:
        p = c['portfolio'] or 'No Portfolio'
        if p not in portfolio_counts:
            portfolio_counts[p] = {'total': 0, 'active_spend': 0, 'spend': 0, 'sales': 0}
        portfolio_counts[p]['total'] += 1
        if c['spend'] > 0:
            portfolio_counts[p]['active_spend'] += 1
        portfolio_counts[p]['spend'] += c['spend']
        portfolio_counts[p]['sales'] += c['sales']

    portfolio_html = ""
    for p, data in sorted(portfolio_counts.items(), key=lambda x: x[1]['spend'], reverse=True):
        acos = (data['spend'] / data['sales'] * 100) if data['sales'] > 0 else None
        acos_str = fmt_pct(acos) if acos is not None else '—'
        ac = acos_color(acos)
        portfolio_html += f"""<tr>
            <td>{p}</td>
            <td style="text-align:right">{data['total']}</td>
            <td style="text-align:right">{data['active_spend']}</td>
            <td style="text-align:right">{fmt_money(data['spend'])}</td>
            <td style="text-align:right">{fmt_money(data['sales'])}</td>
            <td style="text-align:right;color:{ac};font-weight:600">{acos_str}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Harlo Amazon Ads Audit — Interconnections</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Archivo:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    :root {{
        --primary: #5F9598;
        --accent: #B6D7D8;
        --dark: #1e2328;
        --bg: #FAFAFA;
        --white: #FFFFFF;
        --border: #CCCCCC;
        --muted: #6C6C6C;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ background:var(--bg); color:var(--dark); font-family: 'Archivo', Calibri, sans-serif; font-size:11pt; line-height:1.5; }}
    .container {{ max-width:960px; margin:0 auto; padding:32px 24px; }}

    /* Header */
    .report-header {{
        background: var(--dark);
        padding: 48px 40px 40px;
        border-radius: 12px;
        margin-bottom: 32px;
        position: relative;
    }}
    .report-header .logo-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 28px;
    }}
    .report-header .harlo-logo {{ height: 44px; }}
    .report-header .agency-badge {{
        font-family: 'Archivo', sans-serif;
        font-size: 9pt;
        color: var(--accent);
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}
    .report-header h1 {{
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 28pt;
        font-weight: 700;
        color: var(--white);
        line-height: 1.2;
        margin-bottom: 8px;
    }}
    .report-header .subtitle {{
        color: var(--accent);
        font-size: 11pt;
        font-weight: 400;
    }}
    .report-header .accent-line {{
        width: 80px;
        height: 3px;
        background: linear-gradient(90deg, #B6D7D8, #5F9598);
        margin-top: 20px;
        border-radius: 2px;
    }}

    /* Typography */
    h2 {{
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 16pt;
        font-weight: 600;
        color: var(--dark);
        margin: 40px 0 16px;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--accent);
        line-height: 1.2;
    }}
    h3 {{
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 13pt;
        font-weight: 600;
        margin: 28px 0 12px;
        color: var(--primary);
        line-height: 1.2;
    }}
    p {{ margin-bottom: 12px; }}

    /* KPI Cards */
    .kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:16px; margin:20px 0; }}
    .kpi {{
        background:var(--white);
        border:1px solid var(--border);
        border-radius:8px;
        padding:20px;
        text-align:center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    .kpi-highlight {{ border-top: 3px solid var(--primary); }}
    .kpi .label {{ color:var(--muted); font-size:9pt; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px; }}
    .kpi .value {{ font-size:1.6em; font-weight:700; color:var(--dark); }}
    .kpi .sub {{ font-size:9pt; color:var(--muted); margin-top:4px; }}

    /* Cards */
    .card {{
        background:var(--white);
        border:1px solid var(--border);
        border-radius:8px;
        padding:24px;
        margin:16px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}

    /* Alerts — on-brand, no reds/greens/yellows */
    .alert {{
        border-left:4px solid var(--dark);
        background: var(--white);
        padding:16px 20px;
        border-radius:0 8px 8px 0;
        margin:16px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    .alert-warn {{
        border-left-color: var(--primary);
        background: rgba(182,215,216,0.15);
    }}
    .alert-good {{
        border-left-color: var(--accent);
        background: rgba(182,215,216,0.1);
    }}
    .alert strong {{ display:block; margin-bottom:4px; font-weight:700; }}

    /* Tables */
    table {{ width:100%; border-collapse:collapse; font-size:0.85em; }}
    th {{
        background: var(--dark);
        color: var(--white);
        font-weight:600;
        text-align:left;
        padding:10px 12px;
        border-bottom:2px solid var(--border);
        white-space:nowrap;
    }}
    td {{ padding:8px 12px; border-bottom:1px solid var(--border); }}
    tr:nth-child(even) {{ background: var(--bg); }}
    tr:nth-child(odd) {{ background: var(--white); }}
    tr:hover {{ background: rgba(182,215,216,0.15); }}
    .overflow-x {{ overflow-x:auto; }}

    /* Layout */
    .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
    @media (max-width:900px) {{ .two-col {{ grid-template-columns:1fr; }} }}

    /* Tags */
    .tag {{ display:inline-block; padding:2px 8px; border-radius:4px; font-size:9pt; font-weight:600; }}
    .tag-teal {{ background:rgba(95,149,152,0.15); color:#5F9598; }}
    .tag-dark {{ background:rgba(30,35,40,0.1); color:#1e2328; }}
    .tag-accent {{ background:rgba(182,215,216,0.3); color:#5F9598; }}
    .tag-loss {{ background:#1e2328; color:#fff; padding:2px 8px; border-radius:3px; }}

    /* Recommendation Boxes */
    .rec-box {{
        background:var(--white);
        border:1px solid var(--border);
        border-radius:8px;
        padding:20px 24px;
        margin:12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    .rec-box h4 {{
        color:var(--primary);
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 13pt;
        margin-bottom:8px;
    }}
    .rec-box ul {{ margin-left:18px; }}
    .rec-box li {{ margin-bottom:6px; line-height:1.5; }}

    /* Table of Contents */
    .toc {{
        background:var(--white);
        border:1px solid var(--border);
        border-radius:8px;
        padding:24px 28px;
        margin:0 0 32px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    .toc ol {{ margin-left:20px; }}
    .toc li {{ margin:8px 0; }}
    .toc a {{ color:var(--primary); text-decoration:none; font-weight:500; }}
    .toc a:hover {{ text-decoration:underline; }}

    /* Footer */
    .footer {{
        background: var(--dark);
        color: var(--accent);
        text-align:center;
        font-size:9pt;
        margin-top:48px;
        padding:32px 24px;
        border-radius:8px;
    }}
    .footer a {{ color: var(--white); text-decoration:none; font-weight:600; }}
    .footer a:hover {{ text-decoration:underline; }}
    .footer .divider {{ color: var(--muted); margin: 0 8px; }}

    /* Breakeven indicator */
    .breakeven-tag {{
        display:inline-block;
        background: var(--dark);
        color: var(--white);
        font-size:9pt;
        font-weight:700;
        padding:2px 8px;
        border-radius:3px;
    }}

    /* Section dividers */
    hr.section-divider {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #B6D7D8, #5F9598);
        margin: 32px 0;
    }}

    /* Print */
    @media print {{
        body {{ font-size:10pt; }}
        .report-header {{ background: var(--dark) !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        .container {{ max-width:100%; padding:0; }}
        .kpi, .card, .rec-box, .toc {{ box-shadow:none; }}
    }}
</style>
</head>
<body>
<div class="container">

<!-- Report Header -->
<div class="report-header">
    <div class="logo-row">
        <img src="https://drinkharlo.com/cdn/shop/files/harlo_logo_white.png?v=1701873294&width=600" alt="Harlo" class="harlo-logo">
        <div class="agency-badge">Prepared by Interconnections</div>
    </div>
    <h1>Amazon Ads Audit</h1>
    <p class="subtitle">Reporting Period: February 1 – March 19, 2026 &nbsp;&bull;&nbsp; Generated {datetime.now().strftime('%B %d, %Y')}</p>
    <div class="accent-line"></div>
</div>

<div class="toc">
<strong style="font-family:'Playfair Display',Georgia,serif;font-size:13pt;">Table of Contents</strong>
<ol>
<li><a href="#exec">Executive Summary</a></li>
<li><a href="#kpis">Account Overview & KPIs</a></li>
<li><a href="#targets">ACOS / ROAS Target Framework</a></li>
<li><a href="#structure">Campaign Structure Analysis</a></li>
<li><a href="#performance">Campaign Performance Breakdown</a></li>
<li><a href="#branded">Branded vs Non-Branded Split</a></li>
<li><a href="#products">Product-Level Performance</a></li>
<li><a href="#placements">Placement Analysis</a></li>
<li><a href="#search">Search Term Analysis</a></li>
<li><a href="#bids">Bid Optimization</a></li>
<li><a href="#perpetua">Perpetua AI Platform Assessment</a></li>
<li><a href="#buybox">Business Report & Buy Box Alert</a></li>
<li><a href="#recs">Strategic Recommendations</a></li>
</ol>
</div>

<!-- ========== 1. EXECUTIVE SUMMARY ========== -->
<h2 id="exec">1. Executive Summary</h2>
<div class="card">
<p>Harlo spent <strong>{fmt_money(total_spend)}</strong> across all Amazon ad types during Feb 1 – Mar 19, generating <strong>{fmt_money(total_sales)}</strong> in attributed sales at an overall <strong>{fmt_pct(overall_acos)} ACOS</strong> ({overall_roas:.2f}x ROAS). With a <strong>40% breakeven ACOS</strong>, the account is losing money on advertising at current levels — the overall ACOS is {fmt_pct(overall_acos - 40)} above breakeven. The account is heavily reliant on branded search: {fmt_pct(branded_sales/total_sales*100 if total_sales > 0 else 0)} of ad-attributed sales come from branded campaigns (14.5% ACOS — profitable), while non-branded campaigns operate at 85.4% ACOS — burning ~$0.53 for every $1 spent.</p>

<div style="margin-top:16px;">
<p><strong>Three critical issues demand immediate action:</strong></p>
<ol style="margin-left:20px;margin-top:8px;">
<li style="margin-bottom:8px;"><strong>HLP Audience Auto campaign hemorrhaging budget.</strong> A single auto campaign (HLP Audience - Jars) is consuming <strong>{fmt_money(active_campaigns[0]['spend'] if active_campaigns else 0)}</strong> ({fmt_pct(active_campaigns[0]['spend']/total_spend*100 if active_campaigns and total_spend > 0 else 0)} of total spend) at 113% ACOS. This needs to be paused or drastically restructured immediately.</li>
<li style="margin-bottom:8px;"><strong>Buy Box percentage dropped sharply in March</strong> — from {fmt_pct(feb_avg_bb)} average in February to {fmt_pct(mar_avg_bb)} in March, with lows hitting 84.9%. This means Harlo is paying for ad clicks that may not result in the sale going to Harlo.</li>
<li style="margin-bottom:8px;"><strong>Extreme campaign fragmentation.</strong> The account has {total_campaigns} total campaigns, but only {len(active_campaigns)} have any spend. {zero_spend_campaigns} campaigns have zero impressions or spend. This dilutes budget, makes optimization impossible, and creates massive management overhead.</li>
</ol>
</div>
</div>

<!-- ========== 2. ACCOUNT KPIs ========== -->
<h2 id="kpis">2. Account Overview & KPIs</h2>
<div class="kpi-grid">
    <div class="kpi kpi-highlight"><div class="label">Total Ad Spend</div><div class="value">{fmt_money(total_spend)}</div><div class="sub">All campaign types</div></div>
    <div class="kpi kpi-highlight"><div class="label">Ad-Attributed Sales</div><div class="value">{fmt_money(total_sales)}</div></div>
    <div class="kpi kpi-highlight"><div class="label">Overall ACOS</div><div class="value"><span class="breakeven-tag">{fmt_pct(overall_acos)}</span></div><div class="sub">Breakeven: 40%</div></div>
    <div class="kpi kpi-highlight"><div class="label">Overall ROAS</div><div class="value">{overall_roas:.2f}x</div><div class="sub">Breakeven: 2.5x</div></div>
    <div class="kpi"><div class="label">Total Orders</div><div class="value">{fmt_num(total_purchases)}</div></div>
    <div class="kpi"><div class="label">Avg CPC</div><div class="value">{fmt_money(overall_cpc)}</div></div>
    <div class="kpi"><div class="label">CTR</div><div class="value">{fmt_pct(overall_ctr)}</div></div>
    <div class="kpi"><div class="label">CVR (Clicks&rarr;Orders)</div><div class="value">{fmt_pct(overall_cvr)}</div></div>
</div>

<h3>Spend by Campaign Type</h3>
<div class="kpi-grid">
    <div class="kpi"><div class="label">Sponsored Products</div><div class="value">{fmt_money(sp_total_spend)}</div><div class="sub">Sales: {fmt_money(sp_total_sales)} | ACOS: {fmt_pct(sp_total_spend/sp_total_sales*100 if sp_total_sales>0 else 0)}</div></div>
    <div class="kpi"><div class="label">Sponsored Brands</div><div class="value">{fmt_money(sb_total_spend)}</div><div class="sub">Sales: {fmt_money(sb_total_sales)} | ACOS: {fmt_pct(sb_total_spend/sb_total_sales*100 if sb_total_sales>0 else 0)}</div></div>
    <div class="kpi"><div class="label">Sponsored Display</div><div class="value">{fmt_money(sd_total_spend)}</div><div class="sub">Sales: {fmt_money(sd_total_sales)} | ACOS: {fmt_pct(sd_total_spend/sd_total_sales*100 if sd_total_sales>0 else 0) if sd_total_sales > 0 else '—'}</div></div>
</div>

<!-- ========== 3. TARGET FRAMEWORK ========== -->
<h2 id="targets">3. ACOS / ROAS Target Framework</h2>
<div class="card">
<p><strong>Breakeven ACOS: 40%.</strong> Any campaign running above 40% ACOS is losing money on every sale. This is the hard ceiling — not a "stretch goal." All targets below are built from this constraint.</p>
<p style="margin-top:8px;">Harlo's 3-in-1 Performance Hydration Drink Mix (Electrolytes + Creatine + Collagen) is available in four flavors. Pricing: Jars at $44.95, Stick Packs at $34.95, 12-Pack Sachets (HVBX) ~$21.95, 4-Pack Sachets (HVPK) ~$19.95. The product has 268 reviews at 4.63 stars.</p>
<table style="margin-top:16px;">
<tr><th>Campaign Type</th><th>ACOS Target</th><th>ROAS Target</th><th>Rationale</th></tr>
<tr><td><span class="tag tag-teal">Branded Defense</span></td><td style="color:var(--primary);font-weight:700">&le; 15%</td><td style="color:var(--primary);font-weight:700">&ge; 6.5x</td><td>Protect brand search at lowest cost. Currently achieving 5.7–14.1% — on track and profitable.</td></tr>
<tr><td><span class="tag tag-dark">Non-Branded Offense</span></td><td style="font-weight:700">&le; 30%</td><td style="font-weight:700">&ge; 3.3x</td><td>Must stay below 40% breakeven. 30% target preserves margin while scaling non-branded.</td></tr>
<tr><td><span class="tag tag-teal">Product Targeting (Defense)</span></td><td style="color:var(--primary);font-weight:700">&le; 20%</td><td style="color:var(--primary);font-weight:700">&ge; 5.0x</td><td>High-intent placement on own/competitor PDPs — should be highly profitable.</td></tr>
<tr><td><span class="tag tag-accent">Auto Discovery</span></td><td style="font-weight:700">&le; 40%</td><td style="font-weight:700">&ge; 2.5x</td><td>Exploratory — acceptable at breakeven for keyword/ASIN discovery only.</td></tr>
<tr><td style="font-weight:700;border-top:2px solid var(--dark)">Overall Account</td><td style="font-weight:700;color:var(--primary);border-top:2px solid var(--dark)">&le; 25%</td><td style="font-weight:700;color:var(--primary);border-top:2px solid var(--dark)">&ge; 4.0x</td><td style="border-top:2px solid var(--dark)">Blended target: branded pulls average down, non-branded must stay under 40%.</td></tr>
</table>
<p style="margin-top:12px;font-size:9pt;color:var(--muted)"><strong>Current account ACOS is {fmt_pct(overall_acos)} — {fmt_pct(overall_acos - 40)} above breakeven.</strong> The account is losing money on advertising at current levels. Branded campaigns (14.5% ACOS) are profitable; non-branded campaigns (85.4% ACOS) are burning ~$0.53 for every $1 spent.</p>
</div>

<!-- ========== 4. CAMPAIGN STRUCTURE ========== -->
<h2 id="structure">4. Campaign Structure Analysis</h2>

<div class="alert">
<strong>Problem: Extreme Campaign Fragmentation</strong>
The account contains <strong>{total_campaigns} campaigns</strong> — {enabled_campaigns} enabled, {paused_campaigns} paused — but only <strong>{len(active_campaigns)}</strong> generated any spend this period. {zero_spend_campaigns} campaigns had zero spend. This fragments data, prevents algorithmic learning, and creates unmanageable optimization overhead.
</div>

<h3>Portfolio Breakdown</h3>
<div class="overflow-x">
<table>
<tr><th>Portfolio</th><th style="text-align:right">Total Campaigns</th><th style="text-align:right">With Spend</th><th style="text-align:right">Spend</th><th style="text-align:right">Sales</th><th style="text-align:right">ACOS</th></tr>
{portfolio_html}
</table>
</div>

<div class="rec-box" style="margin-top:20px;">
<h4>Structure Recommendations</h4>
<ul>
<li><strong>Consolidate campaigns aggressively.</strong> The Jars portfolio alone has 40+ campaigns. Merge by intent: 1 Branded Exact, 1 Branded Broad/Phrase, 1 Non-Branded Phrase, 1 Auto (close+loose), 1 Product Targeting per product line.</li>
<li><strong>Eliminate redundant PT campaigns.</strong> There are 7 separate PT campaigns for 4-Packs and 7 for 12-Packs (PT 1 through PT 7). Consolidate each into a single PT campaign with ad groups organized by targeting strategy.</li>
<li><strong>Fix portfolio naming.</strong> "Bottel" should be "Bottle". Create a proper portfolio structure: Jars, Sachets (rename from product format), Stick Packs, Bottle, Brand Defense.</li>
<li><strong>Archive zero-activity campaigns.</strong> {zero_spend_campaigns} campaigns with no spend should be archived to reduce clutter.</li>
</ul>
</div>

<!-- ========== 5. CAMPAIGN PERFORMANCE ========== -->
<h2 id="performance">5. Campaign Performance Breakdown</h2>

<h3>Top 20 Campaigns by Spend</h3>
<div class="overflow-x">
<table>
<tr><th>Campaign</th><th>Type</th><th>Portfolio</th><th style="text-align:right">Spend</th><th style="text-align:right">Sales</th><th style="text-align:right">ACOS</th><th style="text-align:right">ROAS</th><th style="text-align:right">Orders</th></tr>
{top_camps_html}
</table>
</div>

<h3>Underperforming Campaigns (ACOS > 50% — Well Above 40% Breakeven)</h3>
<div class="overflow-x">
<table>
<tr><th>Campaign</th><th>Type</th><th style="text-align:right">Spend</th><th style="text-align:right">Sales</th><th style="text-align:right">ACOS</th><th style="text-align:right">Clicks</th></tr>
{worst_html}
</table>
</div>

<div class="alert">
<strong>Immediate Action Required: HLP Audience Auto Campaign</strong>
This single campaign spent <strong>{fmt_money(active_campaigns[0]['spend'] if active_campaigns else 0)}</strong> — {fmt_pct(active_campaigns[0]['spend']/total_spend*100 if active_campaigns and total_spend > 0 else 0)} of total account spend — and returned only {fmt_money(active_campaigns[0]['sales'] if active_campaigns else 0)} in sales (113% ACOS). It is running on <strong>Fixed bids</strong> with audience-based auto targeting, which means Amazon is spending aggressively on complements/substitutes with no downward bid adjustment. Switch to Dynamic Down or pause immediately.
</div>

<!-- ========== 6. BRANDED vs NON-BRANDED ========== -->
<h2 id="branded">6. Branded vs Non-Branded Split</h2>
<div class="kpi-grid">
    <div class="kpi" style="border-top:3px solid var(--primary)">
        <div class="label">Branded Spend</div>
        <div class="value">{fmt_money(branded_spend)}</div>
        <div class="sub">Sales: {fmt_money(branded_sales)} | ACOS: <span style="color:var(--primary);font-weight:700">{fmt_pct(branded_spend/branded_sales*100 if branded_sales>0 else 0)}</span></div>
    </div>
    <div class="kpi" style="border-top:3px solid var(--dark)">
        <div class="label">Non-Branded Spend</div>
        <div class="value">{fmt_money(nonbranded_spend)}</div>
        <div class="sub">Sales: {fmt_money(nonbranded_sales)} | ACOS: <span class="breakeven-tag">{fmt_pct(nonbranded_spend/nonbranded_sales*100 if nonbranded_sales>0 else 0)}</span></div>
    </div>
</div>

<h3>Branded Campaign Performance</h3>
<div class="overflow-x">
<table>
<tr><th>Campaign</th><th style="text-align:right">Spend</th><th style="text-align:right">Sales</th><th style="text-align:right">ACOS</th><th style="text-align:right">Orders</th></tr>
{branded_html}
</table>
</div>

<div class="alert alert-warn">
<strong>Branded Dependency Risk</strong>
{fmt_pct(branded_sales/total_sales*100 if total_sales > 0 else 0)} of ad-attributed sales come from branded terms. Branded ACOS is strong at {fmt_pct(branded_spend/branded_sales*100 if branded_sales>0 else 0)}, but non-branded campaigns are failing to acquire new customers profitably. The non-branded blended ACOS of <strong>{fmt_pct(nonbranded_spend/nonbranded_sales*100 if nonbranded_sales>0 else 0)}</strong> — more than 2x the 40% breakeven — means the account is losing money on every non-branded ad dollar. This requires a complete non-branded strategy rethink.
</div>

<!-- ========== 7. PRODUCT PERFORMANCE ========== -->
<h2 id="products">7. Product-Level Performance</h2>
<div class="overflow-x">
<table>
<tr><th>SKU</th><th>ASIN</th><th style="text-align:right">Spend</th><th style="text-align:right">Total Sales</th><th style="text-align:right">ACOS</th><th style="text-align:right">Orders</th><th style="text-align:right">Adv. SKU Sales</th><th style="text-align:right">Other SKU Sales</th></tr>
{product_html}
</table>
</div>

<!-- ========== 8. PLACEMENTS ========== -->
<h2 id="placements">8. Placement Analysis</h2>
<div class="overflow-x">
<table>
<tr><th>Placement</th><th style="text-align:right">Spend</th><th style="text-align:right">Sales</th><th style="text-align:right">ACOS</th><th style="text-align:right">ROAS</th><th style="text-align:right">Clicks</th><th style="text-align:right">Orders</th></tr>
{placement_html}
</table>
</div>

<div class="rec-box">
<h4>Placement Recommendations</h4>
<ul>
<li><strong>Branded campaigns:</strong> Top-of-Search placements perform exceptionally well (7.8–11.7% ACOS). Increase TOS bid adjustments on branded campaigns to capture more branded real estate.</li>
<li><strong>Non-branded campaigns:</strong> Product Page placements are where the budget leaks. The HLP Auto campaign alone spent $125 on Product Pages with 0 ROAS. Reduce Product Page bids or use placement-level bid reductions.</li>
<li><strong>Rest of Search:</strong> Mixed performance. Branded Rest-of-Search is efficient (11.4% ACOS for MMT Branded); non-branded Rest-of-Search is wasteful (181.8% ACOS for HLP Auto). Apply bid modifiers accordingly.</li>
</ul>
</div>

<!-- ========== 9. SEARCH TERMS ========== -->
<h2 id="search">9. Search Term Analysis</h2>

<h3>Profitable Search Terms — Under 40% ACOS (Promote to Manual Exact)</h3>
<div class="overflow-x">
<table>
<tr><th>Search Term</th><th style="text-align:right">Sales</th><th style="text-align:right">Spend</th><th style="text-align:right">ACOS</th><th style="text-align:right">Orders</th></tr>
{winner_html}
</table>
</div>

<h3>Negative Keyword Candidates (Spend ≥ $3, Zero Sales)</h3>
<div class="overflow-x">
<table>
<tr><th>Search Term / ASIN</th><th style="text-align:right">Wasted Spend</th><th style="text-align:right">Clicks</th><th style="text-align:right">Impressions</th></tr>
{negate_html}
</table>
</div>

<div class="rec-box">
<h4>Search Term Recommendations</h4>
<ul>
<li><strong>Add top performers as exact match keywords</strong> in dedicated manual campaigns with optimized bids. Terms like "creatine and electrolytes", "harlo electrolytes collagen", and "creatine and collagen" are converting well and should be scaled.</li>
<li><strong>Negate all ASIN-based search terms</strong> appearing in keyword campaigns where they match as substitutes/complements with zero sales. These are wasting significant budget in auto campaigns.</li>
<li><strong>Negate irrelevant category terms</strong> like generic supplement ASINs, competitor product ASINs with no conversion history, and broad category terms that don't convert (e.g., "pre workout powder", "energy drink powder").</li>
</ul>
</div>

<!-- ========== 10. BID OPTIMIZATION ========== -->
<h2 id="bids">10. Bid Optimization</h2>
<div class="overflow-x">
<table>
<tr><th>Target</th><th>Campaign</th><th style="text-align:right">Bid</th><th style="text-align:right">Suggested</th><th style="text-align:right">Spend</th><th style="text-align:right">Sales</th><th style="text-align:right">ACOS</th><th style="text-align:center">Action</th></tr>
{bid_html}
</table>
</div>

<div class="rec-box">
<h4>Key Bid Actions</h4>
<ul>
<li><strong>"harlo electrolytes" (exact, $3.20 bid):</strong> 54.6% TOS impression share at 16.1% ACOS. Already dominant on branded — no need to increase bid. Maintain current level.</li>
<li><strong>"+harlo" (broad, $3.25 bid):</strong> 41.9% TOS IS at 10.4% ACOS. Strong performer. Consider slight increase to $3.50–$3.75 to capture additional branded traffic.</li>
<li><strong>close-match / loose-match (HLP Auto):</strong> Spending $1,600+$880 with sub-1.0 ROAS. These bids ($1.26–$1.36) need to be cut to $0.50 or the campaign paused entirely.</li>
<li><strong>substitutes (AUTO TEST, $1.83 bid):</strong> 340% ACOS. Pause the substitutes targeting or negate the top-spending substitute ASINs.</li>
<li><strong>"creatine and electrolytes" (phrase, $2.42 bid):</strong> 4.01 ROAS — strong non-branded term. Consider increasing to $3.00–$3.50 to scale.</li>
</ul>
</div>

<!-- ========== 11. PERPETUA ========== -->
<h2 id="perpetua">11. Perpetua AI Platform Assessment</h2>

<div class="alert alert-warn">
<strong>Insufficient Data for Full Assessment</strong>
Perpetua campaigns launched March 18–19 and have only 1–2 days of data. Any performance conclusions would be premature.
</div>

<div class="overflow-x">
<table>
<tr><th>Campaign</th><th style="text-align:right">Spend</th><th style="text-align:right">Sales</th><th style="text-align:right">Impressions</th><th style="text-align:right">Clicks</th><th style="text-align:right">Orders</th></tr>
{perpetua_html}
</table>
</div>

<div class="card">
<p><strong>Early observations:</strong></p>
<ul style="margin-left:18px;margin-top:8px;">
<li><strong>Excessive fragmentation.</strong> Perpetua created 12 sub-campaigns across 2 campaign groups (PERPETUA TEST + PERPETUA STICKS). Each group has Auto, Manual, PAT, Branded Manual, Branded Pat, and Competitor Manual sub-campaigns. This mirrors the existing account's fragmentation problem.</li>
<li><strong>Budget spread too thin.</strong> With $16–$33/day per sub-campaign, none will accumulate enough data for Perpetua's AI to optimize effectively. Minimum recommended daily budget per campaign for Perpetua is $50+.</li>
<li><strong>No portfolio assignment.</strong> All Perpetua campaigns are in "No Portfolio", making it impossible to track their performance against existing portfolio-level budgets.</li>
<li><strong>Recommendation:</strong> Allow 14–21 days of data before evaluating. If keeping Perpetua, consolidate to fewer campaigns with higher budgets and assign to proper portfolios.</li>
</ul>
</div>

<!-- ========== 12. BUSINESS REPORT ========== -->
<h2 id="buybox">12. Business Report & Buy Box Alert</h2>

<div class="kpi-grid">
    <div class="kpi"><div class="label">Total Product Sales</div><div class="value">{fmt_money(biz_total_sales)}</div><div class="sub">Feb 1 – Mar 18</div></div>
    <div class="kpi"><div class="label">Total Units</div><div class="value">{fmt_num(biz_total_units)}</div></div>
    <div class="kpi"><div class="label">Total Sessions</div><div class="value">{fmt_num(biz_total_sessions)}</div></div>
    <div class="kpi"><div class="label">Avg Buy Box %</div><div class="value">{'<span class="breakeven-tag">' + fmt_pct(biz_avg_buy_box) + '</span>' if biz_avg_buy_box < 97 else fmt_pct(biz_avg_buy_box)}</div></div>
    <div class="kpi"><div class="label">Avg Unit Session %</div><div class="value">{fmt_pct(biz_avg_cvr)}</div></div>
</div>

<div class="alert">
<strong>Buy Box Percentage Dropped Significantly in March</strong>
February average Buy Box: <strong>{fmt_pct(feb_avg_bb)}</strong> &rarr; March average: <strong>{fmt_pct(mar_avg_bb)}</strong>. On March 13, Buy Box hit a low of <strong>84.9%</strong>. This means ~15% of the time, another seller or Amazon itself is winning the Buy Box on Harlo's listings. Every ad click during those periods sends the customer to a competitor seller. Investigate: is a 3P seller undercutting pricing? Has Amazon buy box eligibility changed?
</div>

<h3>Daily Business Report</h3>
<div class="overflow-x">
<table>
<tr><th>Date</th><th style="text-align:right">Sales</th><th style="text-align:right">Units</th><th style="text-align:right">Sessions</th><th style="text-align:right">Buy Box %</th><th style="text-align:right">Unit Session %</th></tr>
{biz_html}
</table>
</div>

<!-- ========== 13. STRATEGIC RECOMMENDATIONS ========== -->
<h2 id="recs">13. Strategic Recommendations</h2>

<div class="rec-box">
<h4>1. Immediate: Stop the Bleeding (Week 1)</h4>
<ul>
<li><strong>Pause or restructure the HLP Audience Auto campaign.</strong> It burned {fmt_money(active_campaigns[0]['spend'] if active_campaigns else 0)} at 113% ACOS. Switch to Dynamic Down bidding at minimum, or pause and reallocate budget to performing campaigns.</li>
<li><strong>Pause AUTO TEST MARCH 17.</strong> Dynamic Up & Down bidding on a brand-new auto campaign led to $420 spend at 300% ACOS in just 2 days. This is exactly why Up & Down should not be used on untested campaigns.</li>
<li><strong>Pause NM - SP - Phrase - All Products Test w/o Collagen.</strong> $466 spend → $145 sales (322% ACOS). The phrase-match version of this test is not working — the auto version is performing better.</li>
<li><strong>Investigate Buy Box drop.</strong> Check for unauthorized 3P sellers, pricing issues, or inventory/FBA problems causing Buy Box loss.</li>
</ul>
</div>

<div class="rec-box">
<h4>2. Short-Term: Optimize What's Working (Weeks 2–4)</h4>
<ul>
<li><strong>Scale branded campaigns.</strong> The MMT Branded campaigns (Jars + 12-Pack) are the account's best performers at 14–19% ACOS. Ensure budgets are never limiting and TOS bid adjustments are maximized.</li>
<li><strong>Promote winning search terms.</strong> Move "creatine and electrolytes", "creatine and collagen", "collagen creatine electrolytes", and "harlo electrolytes collagen" to dedicated exact-match campaigns with higher bids.</li>
<li><strong>Implement negative keywords aggressively.</strong> Add the identified negate candidates (above) as exact-match negatives across all auto and broad-match campaigns.</li>
<li><strong>Right-size bids on non-branded.</strong> Most non-branded campaigns have CPCs of $4–$7 while generating sub-1.0 ROAS. Reduce bids to $1.50–$2.50 and let the algorithm find efficient placements.</li>
</ul>
</div>

<div class="rec-box">
<h4>3. Medium-Term: Restructure the Account (Weeks 4–8)</h4>
<ul>
<li><strong>Consolidate to a clean campaign structure:</strong>
    <ul>
    <li>Per product line (Jars, Sachets, Stick Packs, Bottle): 1 Branded Exact, 1 Branded Broad, 1 Non-Branded Phrase, 1 Auto (Discovery), 1 Product Targeting (Defense)</li>
    <li>Account-level: 1 Competitor Conquest campaign, 1 Category campaign</li>
    <li>Target: ~15–20 active campaigns total (down from 100+)</li>
    </ul>
</li>
<li><strong>Standardize bid strategies.</strong> Use Dynamic Down for all manual campaigns. Reserve Fixed bids only for branded defense where you want maximum impression share. Never use Dynamic Up & Down on non-branded campaigns.</li>
<li><strong>Set up dayparting/budget rules.</strong> With limited budget, ensure top-performing campaigns aren't running out of budget mid-day while wasteful campaigns continue spending.</li>
</ul>
</div>

<div class="rec-box">
<h4>4. Campaign Type Recommendations</h4>
<ul>
<li><strong>Sponsored Products (SP):</strong> Should remain the primary spend driver. Focus on exact/phrase match for converting terms, auto for discovery only at controlled bids.</li>
<li><strong>Sponsored Brands (SB):</strong> The HSA headline campaigns and SB Video campaigns show promise (e.g., SB HSA Phrase Branded Stick Packs: $81 spend, $359 sales). Continue running SB for branded visibility and Store traffic.</li>
<li><strong>Sponsored Display (SD):</strong> Currently all paused with $14 total spend. SD retargeting (Views/Purchase remarketing) should be re-evaluated once the SP structure is cleaned up. Low priority for now.</li>
<li><strong>Perpetua:</strong> Give it 2–3 weeks of data before judging. Consolidate to fewer, better-funded campaigns. Do not overlap Perpetua campaigns with existing manual campaigns on the same keywords — this causes internal competition and inflates CPCs.</li>
</ul>
</div>

<hr class="section-divider">

<div class="card" style="border-top:3px solid var(--primary);margin-top:32px;">
<h3 style="margin-top:0;">Next Steps</h3>
<p>This audit identifies $4,500+ in monthly wasted ad spend and a clear path to bring the account below the 40% ACOS breakeven. The highest-impact moves — pausing the HLP Auto campaign, restructuring non-branded targeting, and resolving the Buy Box issue — can be implemented within the first two weeks.</p>
<p>The logical next step is a full-funnel diagnostic to build a restructured campaign architecture, set keyword-level bids, and establish a 60-day optimization roadmap. That is exactly what we do in our <strong>Growth Diagnostic Sprint</strong>.</p>
<p style="margin-top:16px;margin-bottom:0;"><strong>Abhinav Singh</strong> &bull; Founder, Interconnections<br>
<span style="color:var(--muted);font-size:9pt;"><a href="https://theinterconnections.com" style="color:var(--primary);text-decoration:none;">theinterconnections.com</a></span></p>
</div>

<div class="footer">
    <div style="font-family:'Playfair Display',Georgia,serif;font-size:13pt;color:var(--white);margin-bottom:4px;">Interconnections</div>
    <div style="margin-bottom:12px;">Growth strategy for brands that want to scale profitably, not just grow.</div>
    <div>
        <a href="https://theinterconnections.com">theinterconnections.com</a>
        <span class="divider">|</span>
        Harlo Amazon Ads Audit
        <span class="divider">|</span>
        {datetime.now().strftime('%B %d, %Y')}
    </div>
</div>

</div>
</body>
</html>"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"Harlo_Amazon_Audit_{datetime.now().strftime('%Y-%m-%d')}.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Report generated: {output_path}")
    print(f"\nAccount Summary:")
    print(f"  Total Spend: {fmt_money(total_spend)}")
    print(f"  Total Sales: {fmt_money(total_sales)}")
    print(f"  Overall ACOS: {fmt_pct(overall_acos)}")
    print(f"  Overall ROAS: {overall_roas:.2f}x")
    print(f"  Total Campaigns: {total_campaigns} ({enabled_campaigns} enabled, {paused_campaigns} paused)")
    print(f"  Branded ACOS: {fmt_pct(branded_spend/branded_sales*100 if branded_sales>0 else 0)}")
    print(f"  Non-Branded ACOS: {fmt_pct(nonbranded_spend/nonbranded_sales*100 if nonbranded_sales>0 else 0)}")

if __name__ == '__main__':
    main()
