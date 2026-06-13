#!/usr/bin/env python3
"""
U.S. Clean Energy & Power Infrastructure Research Workbench
Data fetching pipeline.
Uses yfinance for market data, OHLCV, fundamentals, analyst ratings, and news.
Saves raw JSON artifacts for downstream Excel and HTML generation.
"""

import json
import os
import time
import math
from datetime import datetime, timezone, timedelta
from collections import OrderedDict

import yfinance as yf
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_TS = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
REPORT_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Reference pool as provided by the brief
REFERENCE_POOL = [
    "NEE", "FSLR", "ENPH", "SEDG", "TSLA", "ALB", "NXT", "BE",
    "CEG", "VST", "NRG", "GEV", "ETN", "PWR", "FLNC", "STEM",
    "AES", "BEP", "RUN"
]

# Theme segment taxonomy used for watchlist grouping
SEGMENTS = OrderedDict([
    ("Solar / Inverters / Tracking", ["FSLR", "ENPH", "SEDG", "NXT", "RUN"]),
    ("Batteries / EV / Materials",    ["TSLA", "ALB", "FLNC", "STEM", "BE"]),
    ("Grid / Power Equipment",        ["GEV", "ETN", "PWR"]),
    ("Nuclear / IPP / Utility / Data-Center Power", ["NEE", "CEG", "VST", "NRG", "AES", "BEP"]),
])

CUTOFF_NEWS_DAYS = 30


def safe_info(ticker_obj, max_retries=2):
    """Fetch .info with simple retry and return empty dict on failure."""
    for attempt in range(max_retries + 1):
        try:
            info = ticker_obj.info or {}
            if info:
                return info
        except Exception as e:
            print(f"  info retry {attempt+1} for {ticker_obj.ticker}: {e}")
            time.sleep(1.5)
    return {}


def safe_history(ticker_obj, period="6mo", interval="1d", max_retries=2):
    """Fetch price history with retry."""
    for attempt in range(max_retries + 1):
        try:
            hist = ticker_obj.history(period=period, interval=interval)
            if hist is not None and not hist.empty:
                return hist
        except Exception as e:
            print(f"  history retry {attempt+1} for {ticker_obj.ticker}: {e}")
            time.sleep(1.5)
    return pd.DataFrame()


def safe_financials(ticker_obj, max_retries=2):
    """Fetch annual/quarterly financial statements."""
    out = {
        "income_stmt": pd.DataFrame(),
        "quarterly_income_stmt": pd.DataFrame(),
        "balance_sheet": pd.DataFrame(),
        "quarterly_balance_sheet": pd.DataFrame(),
        "cashflow": pd.DataFrame(),
        "quarterly_cashflow": pd.DataFrame(),
    }
    for attempt in range(max_retries + 1):
        try:
            out["income_stmt"] = ticker_obj.income_stmt
            out["quarterly_income_stmt"] = ticker_obj.quarterly_income_stmt
            out["balance_sheet"] = ticker_obj.balance_sheet
            out["quarterly_balance_sheet"] = ticker_obj.quarterly_balance_sheet
            out["cashflow"] = ticker_obj.cashflow
            out["quarterly_cashflow"] = ticker_obj.quarterly_cashflow
            return out
        except Exception as e:
            print(f"  financials retry {attempt+1} for {ticker_obj.ticker}: {e}")
            time.sleep(1.5)
    return out


def safe_news(ticker_obj, max_retries=2):
    """Fetch Yahoo Finance news stream."""
    for attempt in range(max_retries + 1):
        try:
            news = ticker_obj.news or []
            return news
        except Exception as e:
            print(f"  news retry {attempt+1} for {ticker_obj.ticker}: {e}")
            time.sleep(1.5)
    return []


def clean_num(x):
    """Convert numpy/pandas types to JSON-safe Python values."""
    if x is None:
        return None
    if isinstance(x, (np.integer, np.int64, np.int32)):
        return int(x)
    if isinstance(x, (np.floating, np.float64, np.float32)):
        if math.isnan(x) or math.isinf(x):
            return None
        return float(x)
    if isinstance(x, pd.Timestamp):
        return x.isoformat()
    if isinstance(x, datetime):
        return x.isoformat()
    return x


def clean_dict(d):
    """Recursively clean a dict for JSON serialization."""
    if isinstance(d, dict):
        return {k: clean_dict(v) for k, v in d.items()}
    if isinstance(d, list):
        return [clean_dict(v) for v in d]
    return clean_num(d)


def extract_first_value(df, candidates, fallback=None):
    """Extract the most recent non-null value from a financial statement df."""
    if df is None or df.empty:
        return fallback
    for c in candidates:
        if c in df.index:
            s = df.loc[c]
            s = s.replace({np.nan: None})
            for v in s:
                if v is not None and not (isinstance(v, float) and math.isnan(v)):
                    return float(v) if isinstance(v, (int, float, np.floating, np.integer)) else v
    return fallback


def pct_change(series):
    """Return percentage change from first to last value in a series (handles NaN)."""
    s = series.dropna()
    if len(s) < 2:
        return None
    first, last = s.iloc[0], s.iloc[-1]
    if first == 0 or first is None:
        return None
    return (last - first) / first


def main():
    print(f"=== Research Workbench Data Fetch | {REPORT_TS} ===")
    os.makedirs(os.path.join(OUT_DIR, "raw"), exist_ok=True)

    # -----------------------------------------------------------------------
    # 1. Screen all candidates
    # -----------------------------------------------------------------------
    candidate_screen = []
    print("\n[1] Screening reference pool...")
    for ticker in REFERENCE_POOL:
        print(f"  {ticker}", end="")
        obj = yf.Ticker(ticker)
        info = safe_info(obj)
        hist = safe_history(obj, period="6mo", interval="1d")
        fin = safe_financials(obj)
        news = safe_news(obj)

        sector = info.get("sector") or info.get("industry") or "Unknown"
        industry = info.get("industry") or "Unknown"
        name = info.get("longName") or info.get("shortName") or ticker
        price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
        mkt_cap = info.get("marketCap")
        trailing_pe = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        ps = info.get("priceToSalesTrailing12Months")
        pb = info.get("priceToBook")
        ev_ebitda = info.get("enterpriseToEbitda")
        beta = info.get("beta")
        rec_key = info.get("recommendationKey")
        rec_mean = info.get("recommendationMean")
        target_price = info.get("targetMeanPrice") or info.get("targetHighPrice")
        analyst_count = info.get("numberOfAnalystOpinions")
        short_pct = info.get("shortPercentOfFloat")
        div_yield = info.get("dividendYield")
        exchg = info.get("exchange") or info.get("primaryExchange") or "Unknown"
        currency = info.get("currency") or "USD"
        fifty_two_week_low = info.get("fiftyTwoWeekLow")
        fifty_two_week_high = info.get("fiftyTwoWeekHigh")
        avg_volume = info.get("averageVolume") or info.get("averageVolume10days")
        volume = info.get("volume") or info.get("regularMarketVolume")

        # Business summary for exposure validation
        summary = info.get("longBusinessSummary", "")

        # Price momentum
        if not hist.empty:
            latest = float(hist["Close"].iloc[-1]) if not pd.isna(hist["Close"].iloc[-1]) else None
            start_1m = hist["Close"].iloc[-min(21, len(hist)):].iloc[0] if len(hist) >= 5 else None
            chg_1m = (latest - start_1m) / start_1m if (latest and start_1m) else None
            start_3m = hist["Close"].iloc[-min(63, len(hist)):].iloc[0] if len(hist) >= 20 else None
            chg_3m = (latest - start_3m) / start_3m if (latest and start_3m) else None
            ma20 = float(hist["Close"].rolling(20).mean().iloc[-1]) if len(hist) >= 20 else None
            ma50 = float(hist["Close"].rolling(50).mean().iloc[-1]) if len(hist) >= 50 else None
        else:
            latest, chg_1m, chg_3m, ma20, ma50 = None, None, None, None, None

        # Segment assignment
        assigned_segment = "Other"
        for seg, tickers in SEGMENTS.items():
            if ticker in tickers:
                assigned_segment = seg
                break

        # Theme relevance score (simple keyword check)
        keywords = [
            "solar", "renewable", "energy storage", "battery", "lithium",
            "grid", "power", "nuclear", "uranium", "data center", "inverter",
            "utility", "infrastructure", "clean energy", "carbon", "electric vehicle",
            "charging", "photovoltaic", "wind", "electrification"
        ]
        summary_lower = summary.lower()
        relevance_score = sum(1 for kw in keywords if kw in summary_lower)

        # Data completeness score
        dc_fields = [price, mkt_cap, trailing_pe, forward_pe, latest, volume]
        data_completeness = sum(1 for f in dc_fields if f is not None) / len(dc_fields)

        screen_rec = {
            "ticker": ticker,
            "company_name": name,
            "segment": assigned_segment,
            "exchange": exchg,
            "currency": currency,
            "sector": sector,
            "industry": industry,
            "latest_price": clean_num(latest),
            "market_cap": clean_num(mkt_cap),
            "price": clean_num(price),
            "volume": clean_num(volume),
            "avg_volume": clean_num(avg_volume),
            "trailing_pe": clean_num(trailing_pe),
            "forward_pe": clean_num(forward_pe),
            "ps_ratio": clean_num(ps),
            "pb_ratio": clean_num(pb),
            "ev_ebitda": clean_num(ev_ebitda),
            "beta": clean_num(beta),
            "recommendation_key": rec_key,
            "recommendation_mean": clean_num(rec_mean),
            "target_price": clean_num(target_price),
            "analyst_count": clean_num(analyst_count),
            "short_pct_float": clean_num(short_pct),
            "dividend_yield": clean_num(div_yield),
            "fifty_two_week_low": clean_num(fifty_two_week_low),
            "fifty_two_week_high": clean_num(fifty_two_week_high),
            "chg_1m": clean_num(chg_1m),
            "chg_3m": clean_num(chg_3m),
            "ma20": clean_num(ma20),
            "ma50": clean_num(ma50),
            "relevance_score": relevance_score,
            "data_completeness": data_completeness,
            "business_summary": summary[:500] + ("..." if len(summary) > 500 else ""),
            "history_rows": len(hist),
            "has_income_stmt": not fin["income_stmt"].empty,
            "has_balance_sheet": not fin["balance_sheet"].empty,
            "has_cashflow": not fin["cashflow"].empty,
            "news_count": len(news),
        }
        candidate_screen.append(screen_rec)
        print(f" OK (relevance={relevance_score}, completeness={data_completeness:.2f}, hist={len(hist)})")
        time.sleep(0.4)

    # -----------------------------------------------------------------------
    # 2. Selection logic
    # -----------------------------------------------------------------------
    print("\n[2] Selecting final universe...")
    # Required criteria:
    # - theme relevance score >= 1 (some clean-energy keyword in summary)
    # - price history available
    # - data completeness >= 0.5
    eligible = [c for c in candidate_screen
                if c["relevance_score"] >= 1
                and c["history_rows"] >= 20
                and c["data_completeness"] >= 0.5]

    # Composite scoring weights: data completeness 40%, theme relevance 30%,
    # market cap / liquidity proxy 20%, analyst coverage / market attention 10%.
    def composite(c):
        mcap_score = 0
        if c["market_cap"]:
            mcap_score = min(math.log10(c["market_cap"]) / 12, 1.0)  # normalize roughly
        attention_score = 0
        if c["analyst_count"]:
            attention_score = min(c["analyst_count"] / 30, 1.0)
        return (
            c["data_completeness"] * 0.40
            + min(c["relevance_score"] / 5, 1.0) * 0.30
            + mcap_score * 0.20
            + attention_score * 0.10
        )

    eligible_sorted = sorted(eligible, key=composite, reverse=True)

    # First, guarantee at least one representative from each segment to preserve theme coverage.
    final_tickers = []
    segment_pool = {seg: [c for c in eligible_sorted if c["segment"] == seg] for seg in SEGMENTS.keys()}
    for seg in SEGMENTS.keys():
        if segment_pool[seg]:
            top = segment_pool[seg][0]["ticker"]
            if top not in final_tickers:
                final_tickers.append(top)

    # Fill remaining slots by composite score.
    for c in eligible_sorted:
        if c["ticker"] not in final_tickers:
            final_tickers.append(c["ticker"])
        if len(final_tickers) >= 10:
            break

    final_tickers = final_tickers[:10]
    print(f"    Final selections ({len(final_tickers)}): {', '.join(final_tickers)}")

    # Build selection rationale records
    selections = []
    for c in candidate_screen:
        selected = c["ticker"] in final_tickers
        reason = []
        if selected:
            reason.append("High theme relevance")
            if c["data_completeness"] >= 0.8:
                reason.append("Strong data completeness")
            if c["market_cap"] and c["market_cap"] >= 10e9:
                reason.append("Large-cap liquidity")
            reason.append(f"Segment representative ({c['segment']})")
        else:
            # In-eligible cases
            if c["relevance_score"] < 1:
                reason.append("Low theme relevance")
            if c["data_completeness"] < 0.5:
                reason.append("Incomplete market data")
            if c["history_rows"] < 20:
                reason.append("Insufficient price history")
            # Eligible but not in top composite/segment slots
            if not reason:
                reason.append("Eligible but ranked below top composite/segment slots")
                if c["market_cap"] and c["market_cap"] < 5e9:
                    reason.append("Smaller-cap liquidity profile")
        selections.append({
            **c,
            "selected": selected,
            "selection_rationale": "; ".join(reason),
        })

    # -----------------------------------------------------------------------
    # 3. Fetch full data for final selections
    # -----------------------------------------------------------------------
    print("\n[3] Fetching full data for selected universe...")
    final_data = {}
    ohlcv_records = []
    all_news = []

    for ticker in final_tickers:
        print(f"  {ticker}", end="")
        obj = yf.Ticker(ticker)
        info = safe_info(obj)
        hist = safe_history(obj, period="1y", interval="1d")
        fin = safe_financials(obj)
        news = safe_news(obj)

        # Financial metrics extraction
        inc = fin["income_stmt"]
        qinc = fin["quarterly_income_stmt"]
        bs = fin["balance_sheet"]
        cf = fin["cashflow"]
        qcf = fin["quarterly_cashflow"]

        # Revenue (TTM approximation from quarterly)
        revenue_ttm = None
        if not qinc.empty:
            rev_row = qinc.loc["Total Revenue"] if "Total Revenue" in qinc.index else None
            if rev_row is None and "Revenue" in qinc.index:
                rev_row = qinc.loc["Revenue"]
            if rev_row is not None:
                rev_row = rev_row.replace({np.nan: 0})
                revenue_ttm = float(rev_row.iloc[:4].sum()) if len(rev_row) >= 4 else float(rev_row.iloc[:1].sum())

        # Annual revenue trend
        revenue_trend = {}
        if not inc.empty:
            rev_idx = "Total Revenue" if "Total Revenue" in inc.index else ("Revenue" if "Revenue" in inc.index else None)
            if rev_idx:
                for col in inc.columns:
                    dt = pd.Timestamp(col).strftime("%Y-%m-%d") if isinstance(col, (pd.Timestamp, datetime)) else str(col)[:10]
                    val = inc.loc[rev_idx, col]
                    revenue_trend[dt] = clean_num(val)

        # Margins
        gross_margin = None
        net_margin = None
        if not inc.empty:
            rev = extract_first_value(inc, ["Total Revenue", "Revenue"], 0)
            gp = extract_first_value(inc, ["Gross Profit"], 0)
            ni = extract_first_value(inc, ["Net Income", "Net Income Common Stockholders"], 0)
            if rev and rev > 0:
                gross_margin = gp / rev if gp else None
                net_margin = ni / rev if ni else None

        # Cash flow / capex
        operating_cf = extract_first_value(cf, ["Operating Cash Flow", "Total Cash From Operating Activities"])
        capex = extract_first_value(cf, ["Capital Expenditure", "Capital Expenditures"])
        free_cash_flow = None
        if operating_cf is not None and capex is not None:
            free_cash_flow = operating_cf - abs(capex) if capex < 0 else operating_cf - capex

        # Balance sheet risk items
        total_debt = extract_first_value(bs, ["Total Debt"])
        total_cash = extract_first_value(bs, ["Cash And Cash Equivalents", "Cash Financial"])
        total_assets = extract_first_value(bs, ["Total Assets"])
        total_liabilities = extract_first_value(bs, ["Total Liabilities Net Minority Interest", "Total Liabilities"])
        inventory = extract_first_value(bs, ["Inventory"])
        receivables = extract_first_value(bs, ["Net Receivables", "Accounts Receivable"])
        current_assets = extract_first_value(bs, ["Current Assets"])
        current_liabilities = extract_first_value(bs, ["Current Liabilities"])
        quick_ratio = None
        if current_assets is not None and inventory is not None and current_liabilities:
            quick_ratio = (current_assets - inventory) / current_liabilities
        debt_to_assets = total_debt / total_assets if (total_debt and total_assets) else None

        # Earnings / EPS
        eps = info.get("trailingEps") or info.get("forwardEps")
        revenue_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")
        profit_margin = info.get("profitMargins")
        ebitda = info.get("ebitda")
        enterprise_value = info.get("enterpriseValue")

        # Institutional ownership
        inst_pct = info.get("heldPercentInstitutions")

        # Build OHLCV record
        bars = []
        if not hist.empty:
            for idx, row in hist.iterrows():
                bars.append({
                    "date": idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)[:10],
                    "open": clean_num(row.get("Open")),
                    "high": clean_num(row.get("High")),
                    "low": clean_num(row.get("Low")),
                    "close": clean_num(row.get("Close")),
                    "volume": clean_num(row.get("Volume")),
                })
        first_date = bars[0]["date"] if bars else None
        last_date = bars[-1]["date"] if bars else None

        ohlcv_records.append({
            "ticker": ticker,
            "company_name": info.get("longName") or info.get("shortName") or ticker,
            "exchange": info.get("exchange") or info.get("primaryExchange") or "Unknown",
            "currency": info.get("currency") or "USD",
            "data_source": "Yahoo Finance via yfinance",
            "retrieval_timestamp": REPORT_TS,
            "date_range": {"start": first_date, "end": last_date},
            "bars": bars,
        })

        # Process news
        cutoff = datetime.now(timezone.utc) - timedelta(days=CUTOFF_NEWS_DAYS)
        for item in news:
            content = item.get("content") or item
            pub = content.get("pubDate") or content.get("displayTime")
            pub_dt = None
            if pub:
                try:
                    pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                except Exception:
                    pass
            is_recent = pub_dt and pub_dt >= cutoff
            url = (content.get("canonicalUrl") or {}).get("url") or (content.get("clickThroughUrl") or {}).get("url") or ""
            provider = (content.get("provider") or {}).get("displayName") or "Yahoo Finance"
            all_news.append({
                "ticker": ticker,
                "title": content.get("title", ""),
                "source": provider,
                "url": url,
                "pub_date": pub_dt.isoformat() if pub_dt else pub,
                "retrieval_timestamp": REPORT_TS,
                "recent_30d": is_recent,
                "category": "Market/News",
                "why_it_matters": f"Mentions or relates to {ticker}; relevant to clean-energy/power theme monitoring.",
            })

        final_data[ticker] = {
            "info": clean_dict(info),
            "market": {
                "price": clean_num(info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")),
                "previous_close": clean_num(info.get("previousClose")),
                "open": clean_num(info.get("open")),
                "day_high": clean_num(info.get("dayHigh")),
                "day_low": clean_num(info.get("dayLow")),
                "volume": clean_num(info.get("volume") or info.get("regularMarketVolume")),
                "avg_volume": clean_num(info.get("averageVolume") or info.get("averageVolume10days")),
                "market_cap": clean_num(info.get("marketCap")),
                "enterprise_value": clean_num(enterprise_value),
                "fifty_two_week_low": clean_num(info.get("fiftyTwoWeekLow")),
                "fifty_two_week_high": clean_num(info.get("fiftyTwoWeekHigh")),
                "beta": clean_num(info.get("beta")),
                "trailing_pe": clean_num(info.get("trailingPE")),
                "forward_pe": clean_num(info.get("forwardPE")),
                "ps_ratio": clean_num(info.get("priceToSalesTrailing12Months")),
                "pb_ratio": clean_num(info.get("priceToBook")),
                "ev_ebitda": clean_num(info.get("enterpriseToEbitda")),
                "dividend_yield": clean_num(info.get("dividendYield")),
                "target_price": clean_num(info.get("targetMeanPrice")),
                "recommendation_key": info.get("recommendationKey"),
                "recommendation_mean": clean_num(info.get("recommendationMean")),
                "analyst_count": clean_num(info.get("numberOfAnalystOpinions")),
                "short_pct_float": clean_num(info.get("shortPercentOfFloat")),
                "inst_pct": clean_num(inst_pct),
                "revenue_growth": clean_num(revenue_growth),
                "earnings_growth": clean_num(earnings_growth),
                "profit_margin": clean_num(profit_margin),
            },
            "financials": {
                "revenue_ttm": clean_num(revenue_ttm),
                "revenue_trend": revenue_trend,
                "gross_margin": clean_num(gross_margin),
                "net_margin": clean_num(net_margin),
                "ebitda": clean_num(ebitda),
                "eps": clean_num(eps),
                "operating_cash_flow": clean_num(operating_cf),
                "capex": clean_num(capex),
                "free_cash_flow": clean_num(free_cash_flow),
                "total_debt": clean_num(total_debt),
                "total_cash": clean_num(total_cash),
                "total_assets": clean_num(total_assets),
                "total_liabilities": clean_num(total_liabilities),
                "inventory": clean_num(inventory),
                "receivables": clean_num(receivables),
                "current_assets": clean_num(current_assets),
                "current_liabilities": clean_num(current_liabilities),
                "quick_ratio": clean_num(quick_ratio),
                "debt_to_assets": clean_num(debt_to_assets),
            },
            "segment": [s for s, ts in SEGMENTS.items() if ticker in ts][0] if any(ticker in ts for ts in SEGMENTS.values()) else "Other",
            "business_summary": info.get("longBusinessSummary", "")[:600] + ("..." if len(info.get("longBusinessSummary", "")) > 600 else ""),
        }
        print(f" OK ({len(bars)} bars, {len(news)} news items)")
        time.sleep(0.4)

    # -----------------------------------------------------------------------
    # 4. Save artifacts
    # -----------------------------------------------------------------------
    print("\n[4] Saving artifacts...")

    # Raw candidate screening
    with open(os.path.join(OUT_DIR, "raw", "candidate_screen.json"), "w", encoding="utf-8") as f:
        json.dump({
            "report_timestamp": REPORT_TS,
            "reference_pool": REFERENCE_POOL,
            "screening_criteria": {
                "relevance_score_min": 1,
                "history_rows_min": 20,
                "data_completeness_min": 0.5,
            },
            "candidates": selections,
            "final_selections": final_tickers,
        }, f, indent=2)

    # Final company data
    with open(os.path.join(OUT_DIR, "raw", "final_company_data.json"), "w", encoding="utf-8") as f:
        json.dump({
            "report_timestamp": REPORT_TS,
            "data_source": "Yahoo Finance via yfinance",
            "tickers": final_tickers,
            "companies": final_data,
        }, f, indent=2)

    # OHLCV JSON (main deliverable)
    with open(os.path.join(OUT_DIR, "market_ohlcv.json"), "w", encoding="utf-8") as f:
        json.dump({
            "report_timestamp": REPORT_TS,
            "data_source": "Yahoo Finance via yfinance",
            "interval": "1d",
            "period": "1y",
            "records": ohlcv_records,
        }, f, indent=2)

    # News feed
    with open(os.path.join(OUT_DIR, "raw", "news_feed.json"), "w", encoding="utf-8") as f:
        json.dump({
            "report_timestamp": REPORT_TS,
            "news_recency_days": CUTOFF_NEWS_DAYS,
            "items": all_news,
        }, f, indent=2)

    print("\nArtifacts saved:")
    print(f"  - {os.path.join(OUT_DIR, 'raw', 'candidate_screen.json')}")
    print(f"  - {os.path.join(OUT_DIR, 'raw', 'final_company_data.json')}")
    print(f"  - {os.path.join(OUT_DIR, 'market_ohlcv.json')}")
    print(f"  - {os.path.join(OUT_DIR, 'raw', 'news_feed.json')}")
    print("\nDone.")


if __name__ == "__main__":
    main()
