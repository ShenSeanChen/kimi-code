#!/usr/bin/env python3
"""
Build Excel deliverables for the Clean Energy & Power Research Workbench.
"""

import json
import os
import math
from datetime import datetime, timezone

import pandas as pd

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_TS = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fmt_billions(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return round(x / 1e9, 3)


def fmt_millions(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return round(x / 1e6, 3)


def fmt_pct(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return round(x * 100, 2)


def main():
    screen = load_json(os.path.join(OUT_DIR, "raw", "candidate_screen.json"))
    final = load_json(os.path.join(OUT_DIR, "raw", "final_company_data.json"))
    news = load_json(os.path.join(OUT_DIR, "raw", "news_feed.json"))
    ohlcv = load_json(os.path.join(OUT_DIR, "market_ohlcv.json"))

    # -----------------------------------------------------------------------
    # 1. Peer comparison workbook
    # -----------------------------------------------------------------------
    peer_rows = []
    for ticker, data in final["companies"].items():
        m = data["market"]
        f = data["financials"]
        rec_key = m.get("recommendation_key") or "N/A"
        rec_mean = m.get("recommendation_mean")
        rec_str = f"{rec_key} ({rec_mean:.2f})" if rec_mean else rec_key

        peer_rows.append({
            "Ticker": ticker,
            "Company Name": data["info"].get("longName") or data["info"].get("shortName") or ticker,
            "Theme Segment": data["segment"],
            "Exchange": data["info"].get("exchange") or data["info"].get("primaryExchange") or "N/A",
            "Currency": data["info"].get("currency") or "USD",
            "Sector": data["info"].get("sector") or "N/A",
            "Industry": data["info"].get("industry") or "N/A",
            "Latest Price": m.get("price"),
            "Previous Close": m.get("previous_close"),
            "Day High": m.get("day_high"),
            "Day Low": m.get("day_low"),
            "Volume": m.get("volume"),
            "Avg Volume": m.get("avg_volume"),
            "52W High": m.get("fifty_two_week_high"),
            "52W Low": m.get("fifty_two_week_low"),
            "Market Cap ($B)": fmt_billions(m.get("market_cap")),
            "Enterprise Value ($B)": fmt_billions(m.get("enterprise_value")),
            "Beta": m.get("beta"),
            "Trailing P/E": m.get("trailing_pe"),
            "Forward P/E": m.get("forward_pe"),
            "P/S": m.get("ps_ratio"),
            "P/B": m.get("pb_ratio"),
            "EV/EBITDA": m.get("ev_ebitda"),
            "Dividend Yield (%)": fmt_pct(m.get("dividend_yield")),
            "Revenue TTM ($B)": fmt_billions(f.get("revenue_ttm")),
            "Gross Margin (%)": fmt_pct(f.get("gross_margin")),
            "Net Margin (%)": fmt_pct(f.get("net_margin")),
            "Profit Margin (%)": fmt_pct(m.get("profit_margin")),
            "EPS": f.get("eps"),
            "EBITDA ($B)": fmt_billions(f.get("ebitda")),
            "Operating CF ($B)": fmt_billions(f.get("operating_cash_flow")),
            "Capex ($B)": fmt_billions(f.get("capex")),
            "Free Cash Flow ($B)": fmt_billions(f.get("free_cash_flow")),
            "Total Debt ($B)": fmt_billions(f.get("total_debt")),
            "Total Cash ($B)": fmt_billions(f.get("total_cash")),
            "Total Assets ($B)": fmt_billions(f.get("total_assets")),
            "Total Liabilities ($B)": fmt_billions(f.get("total_liabilities")),
            "Inventory ($B)": fmt_billions(f.get("inventory")),
            "Receivables ($B)": fmt_billions(f.get("receivables")),
            "Quick Ratio": f.get("quick_ratio"),
            "Debt/Assets": f.get("debt_to_assets"),
            "Revenue Growth (%)": fmt_pct(m.get("revenue_growth")),
            "Earnings Growth (%)": fmt_pct(m.get("earnings_growth")),
            "Analyst Rec": rec_str,
            "Target Price": m.get("target_price"),
            "Analyst Count": m.get("analyst_count"),
            "Short % Float": fmt_pct(m.get("short_pct_float")),
            "Institutional %": fmt_pct(m.get("inst_pct")),
            "Business Summary": data.get("business_summary", ""),
        })

    peer_df = pd.DataFrame(peer_rows)

    # Revenue trend sheet
    rev_rows = []
    for ticker, data in final["companies"].items():
        for date, val in (data["financials"].get("revenue_trend") or {}).items():
            rev_rows.append({
                "Ticker": ticker,
                "Company": data["info"].get("longName") or ticker,
                "Fiscal Year End": date,
                "Revenue ($B)": fmt_billions(val),
            })
    rev_df = pd.DataFrame(rev_rows).sort_values(["Ticker", "Fiscal Year End"])

    # Candidate screening sheet
    screen_rows = []
    for c in screen["candidates"]:
        screen_rows.append({
            "Ticker": c["ticker"],
            "Company Name": c["company_name"],
            "Segment": c["segment"],
            "Selected": c["selected"],
            "Selection / Exclusion Rationale": c.get("selection_rationale", ""),
            "Relevance Score": c["relevance_score"],
            "Data Completeness": c["data_completeness"],
            "Market Cap ($B)": fmt_billions(c.get("market_cap")),
            "Latest Price": c.get("latest_price"),
            "Chg 1M (%)": fmt_pct(c.get("chg_1m")),
            "Chg 3M (%)": fmt_pct(c.get("chg_3m")),
            "Analyst Count": c.get("analyst_count"),
            "History Rows": c.get("history_rows"),
            "Has Income Stmt": c.get("has_income_stmt"),
            "Has Balance Sheet": c.get("has_balance_sheet"),
            "Has Cashflow": c.get("has_cashflow"),
            "News Count": c.get("news_count"),
            "Business Summary": c.get("business_summary", ""),
        })
    screen_df = pd.DataFrame(screen_rows)

    # News sheet
    news_rows = []
    for item in news["items"]:
        news_rows.append({
            "Ticker": item["ticker"],
            "Title": item["title"],
            "Source": item["source"],
            "URL": item["url"],
            "Publication Date": item.get("pub_date"),
            "Recent 30D": item.get("recent_30d", False),
            "Category": item["category"],
            "Why It Matters": item["why_it_matters"],
            "Retrieval Timestamp": item["retrieval_timestamp"],
        })
    news_df = pd.DataFrame(news_rows).sort_values(["Ticker", "Publication Date"], ascending=[True, False])

    peer_path = os.path.join(OUT_DIR, "us_clean_energy_power_peer_comps.xlsx")
    peer_sheets = {
        "Peer Comps": peer_df,
        "Revenue Trend": rev_df,
        "Screening & Selection": screen_df,
        "News Feed": news_df,
    }
    with pd.ExcelWriter(peer_path, engine="xlsxwriter") as writer:
        for sheet_name, df in peer_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            ws = writer.sheets[sheet_name]
            ws.freeze_panes(1, 0)
            for i, col in enumerate(df.columns):
                max_len = max(len(str(col)), 12)
                ws.set_column(i, i, min(max_len + 2, 50))

    print(f"[Excel] {peer_path}")

    # -----------------------------------------------------------------------
    # 2. Source inventory workbook
    # -----------------------------------------------------------------------
    source_rows = []

    # OHLCV / market data
    for rec in ohlcv["records"]:
        source_rows.append({
            "Source ID": f"YF-OHLCV-{rec['ticker']}",
            "Category": "Market Data",
            "Ticker": rec["ticker"],
            "Description": f"OHLCV daily bars ({rec['date_range']['start']} to {rec['date_range']['end']})",
            "Source Name": rec["data_source"],
            "URL / API": "https://finance.yahoo.com",
            "Local Path": os.path.join(OUT_DIR, "market_ohlcv.json"),
            "Retrieval Timestamp": rec["retrieval_timestamp"],
            "Coverage Start": rec["date_range"]["start"],
            "Coverage End": rec["date_range"]["end"],
            "Rows / Records": len(rec["bars"]),
            "Limitations / Notes": "Yahoo Finance adjusted close; subject to corporate actions.",
        })

    # Company info / fundamentals
    for ticker, data in final["companies"].items():
        source_rows.append({
            "Source ID": f"YF-INFO-{ticker}",
            "Category": "Company Info / Fundamentals",
            "Ticker": ticker,
            "Description": "Company profile, valuation, analyst ratings, ownership",
            "Source Name": "Yahoo Finance via yfinance",
            "URL / API": f"https://finance.yahoo.com/quote/{ticker}",
            "Local Path": os.path.join(OUT_DIR, "raw", "final_company_data.json"),
            "Retrieval Timestamp": final.get("report_timestamp"),
            "Coverage Start": "N/A",
            "Coverage End": "N/A",
            "Rows / Records": "1 profile + financial statement extracts",
            "Limitations / Notes": "Some metrics are TTM or stale; missing values marked null.",
        })

    # News items
    for item in news["items"]:
        source_rows.append({
            "Source ID": f"YF-NEWS-{item['ticker']}-{item['pub_date']}",
            "Category": "News",
            "Ticker": item["ticker"],
            "Description": item["title"][:120],
            "Source Name": item["source"],
            "URL / API": item["url"],
            "Local Path": os.path.join(OUT_DIR, "raw", "news_feed.json"),
            "Retrieval Timestamp": item["retrieval_timestamp"],
            "Coverage Start": item.get("pub_date"),
            "Coverage End": item.get("pub_date"),
            "Rows / Records": 1,
            "Limitations / Notes": "Filtered to 30-day recency where possible; hosted by Yahoo/3rd parties.",
        })

    # Screening pool source
    source_rows.append({
        "Source ID": "INTERNAL-SCREEN",
        "Category": "Methodology",
        "Ticker": "ALL",
        "Description": "Reference pool, screening criteria, selection rationale",
        "Source Name": "Internal research workbench pipeline",
        "URL / API": "N/A",
        "Local Path": os.path.join(OUT_DIR, "raw", "candidate_screen.json"),
        "Retrieval Timestamp": screen.get("report_timestamp"),
        "Coverage Start": "N/A",
        "Coverage End": "N/A",
        "Rows / Records": len(screen["candidates"]),
        "Limitations / Notes": "Screening based on Yahoo Finance data availability and keyword relevance.",
    })

    source_df = pd.DataFrame(source_rows)

    # Data limitations / audit sheet
    audit_rows = [
        {
            "Item": "Report timestamp",
            "Value": REPORT_TS,
            "Notes": "All timestamps in UTC.",
        },
        {
            "Item": "Market data source",
            "Value": "Yahoo Finance via yfinance",
            "Notes": "Prices are adjusted for splits and dividends where applicable.",
        },
        {
            "Item": "OHLCV period",
            "Value": "1 year daily",
            "Notes": "Saved in market_ohlcv.json.",
        },
        {
            "Item": "News recency window",
            "Value": "30 calendar days",
            "Notes": "Older items labeled as background context in HTML.",
        },
        {
            "Item": "Financial statement extracts",
            "Value": "Most recent annual + quarterly",
            "Notes": "Used for margin, cash flow, and balance-sheet risk charts.",
        },
        {
            "Item": "Missing data handling",
            "Value": "JSON null / Excel blank",
            "Notes": "No fabricated values; gaps reflect source limitations.",
        },
        {
            "Item": "Not investment advice",
            "Value": "True",
            "Notes": "No buy/sell/hold recommendations, targets, or position sizing.",
        },
        {
            "Item": "Reference pool size",
            "Value": len(screen["reference_pool"]),
            "Notes": f"Tickers: {', '.join(screen['reference_pool'])}",
        },
        {
            "Item": "Final selections",
            "Value": len(final["tickers"]),
            "Notes": f"Tickers: {', '.join(final['tickers'])}",
        },
        {
            "Item": "Excluded notable names",
            "Value": "FSLR, SEDG, BE, ETN, FLNC, STEM, BEP, RUN",
            "Notes": "Eligible but ranked below top composite/segment slots; see Screening sheet.",
        },
    ]
    audit_df = pd.DataFrame(audit_rows)

    source_path = os.path.join(OUT_DIR, "source_inventory.xlsx")
    source_sheets = {
        "Source Inventory": source_df,
        "Audit & Limitations": audit_df,
    }
    with pd.ExcelWriter(source_path, engine="xlsxwriter") as writer:
        for sheet_name, df in source_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            ws = writer.sheets[sheet_name]
            ws.freeze_panes(1, 0)
            for i, col in enumerate(df.columns):
                max_len = max(len(str(col)), 12)
                ws.set_column(i, i, min(max_len + 2, 60))

    print(f"[Excel] {source_path}")
    print("\nExcel deliverables complete.")


if __name__ == "__main__":
    main()
