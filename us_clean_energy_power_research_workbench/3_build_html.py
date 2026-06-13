#!/usr/bin/env python3
"""
Build research_workbench.html — a Bloomberg Terminal-style interactive dashboard.
Embeds real OHLCV JSON and renders all charts with ECharts.
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


def safe_json(obj):
    """Ensure Python None/nan are JSON null, no invalid JS values."""
    return json.dumps(obj, allow_nan=False)


def fmt_b(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "N/A"
    return f"${x/1e9:.2f}B"


def fmt_pct(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "N/A"
    return f"{x*100:.2f}%"


def main():
    screen = load_json(os.path.join(OUT_DIR, "raw", "candidate_screen.json"))
    final = load_json(os.path.join(OUT_DIR, "raw", "final_company_data.json"))
    news = load_json(os.path.join(OUT_DIR, "raw", "news_feed.json"))
    ohlcv = load_json(os.path.join(OUT_DIR, "market_ohlcv.json"))

    tickers = final["tickers"]
    companies = final["companies"]

    # Prepare ticker tape data
    tape_data = []
    for ticker in tickers:
        m = companies[ticker]["market"]
        tape_data.append({
            "ticker": ticker,
            "name": companies[ticker]["info"].get("shortName") or companies[ticker]["info"].get("longName", ticker),
            "price": m.get("price"),
            "change": None,
            "pct_change": None,
            "volume": m.get("volume"),
            "market_cap": m.get("market_cap"),
        })

    # Compute 1-day change from OHLCV
    for rec in ohlcv["records"]:
        bars = rec["bars"]
        if len(bars) >= 2:
            prev_close = bars[-2].get("close")
            last_close = bars[-1].get("close")
            if prev_close and last_close:
                change = last_close - prev_close
                pct = change / prev_close
                td = next(t for t in tape_data if t["ticker"] == rec["ticker"])
                td["change"] = change
                td["pct_change"] = pct

    # Watchlist grouped by segment
    segments = {}
    for ticker in tickers:
        seg = companies[ticker]["segment"]
        segments.setdefault(seg, []).append(ticker)

    # Representative candlestick tickers (top 5 by market cap)
    cand_tickers = sorted(
        tickers,
        key=lambda t: (companies[t]["market"].get("market_cap") or 0),
        reverse=True,
    )[:5]

    # News items split recent vs background
    recent_news = [n for n in news["items"] if n.get("recent_30d")]
    bg_news = [n for n in news["items"] if not n.get("recent_30d")]

    # Embed data JSON
    ohlcv_json = safe_json(ohlcv)
    final_json = safe_json(final)
    news_json = safe_json(news)
    screen_json = safe_json(screen)
    tape_json = safe_json(tape_data)
    segments_json = safe_json(segments)
    cand_json = safe_json(cand_tickers)

    # Build HTML
    html = build_html(
        ohlcv_json=ohlcv_json,
        final_json=final_json,
        news_json=news_json,
        screen_json=screen_json,
        screen=screen,
        tape_json=tape_json,
        segments_json=segments_json,
        cand_json=cand_json,
        tickers=tickers,
        companies=companies,
        segments=segments,
        recent_news=recent_news,
        bg_news=bg_news,
        tape_data=tape_data,
    )

    html_path = os.path.join(OUT_DIR, "research_workbench.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[HTML] {html_path}")


def build_html(**ctx):
    # Destructure context
    ohlcv_json = ctx["ohlcv_json"]
    final_json = ctx["final_json"]
    news_json = ctx["news_json"]
    screen_json = ctx["screen_json"]
    screen = ctx["screen"]
    tape_json = ctx["tape_json"]
    segments_json = ctx["segments_json"]
    cand_json = ctx["cand_json"]
    tickers = ctx["tickers"]
    companies = ctx["companies"]
    segments = ctx["segments"]
    recent_news = ctx["recent_news"]
    bg_news = ctx["bg_news"]
    tape_data = ctx["tape_data"]

    # Helper: build ticker tape HTML
    tape_items_html = ""
    for t in tape_data:
        color = "up" if (t["pct_change"] or 0) >= 0 else "down"
        sign = "+" if (t["pct_change"] or 0) >= 0 else ""
        pct_str = fmt_pct(t["pct_change"]) if t["pct_change"] is not None else "N/A"
        price_str = f"{t['price']:.2f}" if t["price"] else "N/A"
        vol_str = f"{t['volume']/1e6:.2f}M" if t["volume"] else "N/A"
        tape_items_html += f"""
        <div class="tape-item {color}">
            <span class="t-ticker">{t['ticker']}</span>
            <span class="t-name">{t['name']}</span>
            <span class="t-price">{price_str}</span>
            <span class="t-pct">{sign}{pct_str}</span>
            <span class="t-vol">Vol {vol_str}</span>
        </div>
        """

    # Helper: watchlist rail
    watchlist_html = ""
    for seg, seg_tickers in segments.items():
        watchlist_html += f"""
        <div class="wl-group">
            <div class="wl-group-title">{seg}</div>
        """
        for ticker in seg_tickers:
            m = companies[ticker]["market"]
            price = m.get("price")
            # compute 1d pct from tape_data
            td = next((x for x in tape_data if x["ticker"] == ticker), {})
            pct = td.get("pct_change")
            color = "up" if (pct or 0) >= 0 else "down"
            sign = "+" if (pct or 0) >= 0 else ""
            pct_str = f"{sign}{pct*100:.2f}%" if pct is not None else "N/A"
            price_str = f"${price:.2f}" if price else "N/A"
            watchlist_html += f"""
            <div class="wl-item" data-ticker="{ticker}" onclick="focusTicker('{ticker}')">
                <div class="wl-ticker">{ticker}</div>
                <div class="wl-name">{companies[ticker]['info'].get('shortName') or ticker}</div>
                <div class="wl-meta">
                    <span>{price_str}</span>
                    <span class="{color}">{pct_str}</span>
                </div>
            </div>
            """
        watchlist_html += "</div>"

    # Helper: market snapshot table rows
    snapshot_rows = ""
    for ticker in tickers:
        m = companies[ticker]["market"]
        f = companies[ticker]["financials"]
        td = next((x for x in tape_data if x["ticker"] == ticker), {})
        pct = td.get("pct_change")
        color = "up" if (pct or 0) >= 0 else "down"
        sign = "+" if (pct or 0) >= 0 else ""
        pct_str = f"{sign}{pct*100:.2f}%" if pct is not None else "N/A"
        snapshot_rows += f"""
        <tr>
            <td><strong>{ticker}</strong></td>
            <td>{companies[ticker]['info'].get('shortName') or ticker}</td>
            <td>{companies[ticker]['segment']}</td>
            <td>{m.get('price', 'N/A')}</td>
            <td class="{color}">{pct_str}</td>
            <td>{fmt_b(m.get('market_cap'))}</td>
            <td>{m.get('trailing_pe') if m.get('trailing_pe') else 'N/A'}</td>
            <td>{m.get('forward_pe') if m.get('forward_pe') else 'N/A'}</td>
            <td>{m.get('beta') if m.get('beta') is not None else 'N/A'}</td>
            <td>{fmt_pct(m.get('dividend_yield'))}</td>
            <td>{fmt_b(f.get('revenue_ttm'))}</td>
        </tr>
        """

    # Helper: peer comparison rows
    peer_rows = ""
    for ticker in tickers:
        m = companies[ticker]["market"]
        f = companies[ticker]["financials"]
        peer_rows += f"""
        <tr>
            <td><strong>{ticker}</strong></td>
            <td>{fmt_b(m.get('market_cap'))}</td>
            <td>{m.get('trailing_pe') if m.get('trailing_pe') else 'N/A'}</td>
            <td>{m.get('forward_pe') if m.get('forward_pe') else 'N/A'}</td>
            <td>{m.get('ev_ebitda') if m.get('ev_ebitda') else 'N/A'}</td>
            <td>{m.get('ps_ratio') if m.get('ps_ratio') else 'N/A'}</td>
            <td>{m.get('pb_ratio') if m.get('pb_ratio') else 'N/A'}</td>
            <td>{fmt_pct(f.get('gross_margin'))}</td>
            <td>{fmt_pct(f.get('net_margin'))}</td>
            <td>{fmt_b(f.get('revenue_ttm'))}</td>
            <td>{fmt_b(f.get('operating_cash_flow'))}</td>
            <td>{fmt_b(f.get('free_cash_flow'))}</td>
            <td>{fmt_b(f.get('total_debt'))}</td>
            <td>{f.get('quick_ratio') if f.get('quick_ratio') is not None else 'N/A'}</td>
        </tr>
        """

    # Helper: news feed cards
    def news_card(item, badge_class="recent"):
        return f"""
        <div class="news-card">
            <div class="news-header">
                <span class="news-ticker">{item['ticker']}</span>
                <span class="news-date">{item.get('pub_date', 'N/A')}</span>
                <span class="news-badge {badge_class}">{"30D" if item.get('recent_30d') else "BACKGROUND"}</span>
            </div>
            <div class="news-title"><a href="{item['url']}" target="_blank" rel="noopener">{item['title']}</a></div>
            <div class="news-source">{item['source']} | <a href="{item['url']}" target="_blank" rel="noopener">{item['url']}</a></div>
            <div class="news-why">{item['why_it_matters']}</div>
        </div>
        """

    recent_news_html = "".join(news_card(n, "recent") for n in recent_news[:30])
    bg_news_html = "".join(news_card(n, "background") for n in bg_news[:20])

    # Helper: analyst notes
    analyst_notes = []
    for ticker in tickers:
        m = companies[ticker]["market"]
        f = companies[ticker]["financials"]
        rec = m.get("recommendation_key", "N/A")
        mean = m.get("recommendation_mean")
        target = m.get("target_price")
        price = m.get("price")
        # Agreement / divergence
        if mean and mean <= 2.0:
            analyst_notes.append({"ticker": ticker, "type": "agreement", "text": f"{ticker}: Strong analyst agreement (mean {mean:.2f}) on {rec}."})
        elif mean and mean >= 3.0:
            analyst_notes.append({"ticker": ticker, "type": "divergence", "text": f"{ticker}: Analyst divergence / bearish tilt (mean {mean:.2f})."})
        # Risk flags
        if f.get("net_margin") and f["net_margin"] < 0:
            analyst_notes.append({"ticker": ticker, "type": "risk", "text": f"{ticker}: Negative net margin — profitability pressure."})
        if f.get("free_cash_flow") and f["free_cash_flow"] < 0:
            analyst_notes.append({"ticker": ticker, "type": "risk", "text": f"{ticker}: Negative free cash flow — watch capex vs. cash generation."})
        if f.get("quick_ratio") and f["quick_ratio"] < 0.8:
            analyst_notes.append({"ticker": ticker, "type": "risk", "text": f"{ticker}: Quick ratio below 0.8 — liquidity watch."})
        if m.get("short_pct_float") and m["short_pct_float"] > 0.10:
            analyst_notes.append({"ticker": ticker, "type": "risk", "text": f"{ticker}: Elevated short interest ({fmt_pct(m['short_pct_float'])})."})
        # Watch items
        if target and price:
            upside = (target - price) / price
            analyst_notes.append({"ticker": ticker, "type": "watch", "text": f"{ticker}: Target ${target:.2f} vs price ${price:.2f} (upside {upside*100:+.1f}%)."})

    analyst_html = ""
    for note in analyst_notes:
        analyst_html += f"""
        <div class="note note-{note['type']}">
            <span class="note-ticker">{note['ticker']}</span>
            <span class="note-text">{note['text']}</span>
        </div>
        """

    # Helper: screening table rows
    screen_rows = ""
    for c in json.loads(screen_json)["candidates"]:
        sel_badge = "<span class='badge-selected'>SELECTED</span>" if c["selected"] else "<span class='badge-excluded'>EXCLUDED</span>"
        screen_rows += f"""
        <tr>
            <td><strong>{c['ticker']}</strong></td>
            <td>{c['company_name']}</td>
            <td>{c['segment']}</td>
            <td>{sel_badge}</td>
            <td>{c.get('selection_rationale', '')}</td>
            <td>{c['relevance_score']}</td>
            <td>{c['data_completeness']:.2f}</td>
            <td>{fmt_b(c.get('market_cap'))}</td>
            <td>{fmt_pct(c.get('chg_1m'))}</td>
            <td>{fmt_pct(c.get('chg_3m'))}</td>
        </tr>
        """

    # Helper: data completeness matrix rows
    completeness_rows = ""
    for c in json.loads(screen_json)["candidates"]:
        if c["selected"]:
            completeness_rows += f"""
            <tr>
                <td><strong>{c['ticker']}</strong></td>
                <td>{"✓" if c.get('has_income_stmt') else "—"}</td>
                <td>{"✓" if c.get('has_balance_sheet') else "—"}</td>
                <td>{"✓" if c.get('has_cashflow') else "—"}</td>
                <td>{c['history_rows']}</td>
                <td>{c['news_count']}</td>
                <td>{c['data_completeness']:.2f}</td>
            </tr>
            """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>U.S. Clean Energy & Power Infrastructure — Research Workbench</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0b0f14;
            --panel: #111821;
            --panel-2: #0f151c;
            --border: #1f2a38;
            --text: #e6edf3;
            --text-dim: #8b9aae;
            --accent: #f59e0b;
            --accent-2: #38bdf8;
            --up: #22c55e;
            --down: #ef4444;
            --warn: #f59e0b;
            --risk: #ef4444;
            --agree: #22c55e;
            --diverge: #f59e0b;
        }}
        * {{ box-sizing: border-box; }}
        html, body {{ margin: 0; padding: 0; height: 100%; overflow: hidden; background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; font-size: 13px; display: flex; flex-direction: column; }}
        a {{ color: var(--accent-2); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .mono {{ font-family: 'IBM Plex Mono', monospace; }}
        .up {{ color: var(--up); }}
        .down {{ color: var(--down); }}

        /* Header */
        .terminal-header {{
            height: 54px;
            background: linear-gradient(90deg, #0d131a 0%, #111821 100%);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            padding: 0 16px;
            gap: 16px;
            flex-shrink: 0;
        }}
        .terminal-title {{
            font-weight: 700;
            font-size: 15px;
            color: var(--accent);
            letter-spacing: 0.3px;
            white-space: nowrap;
        }}
        .terminal-subtitle {{ color: var(--text-dim); font-size: 11px; }}
        .header-search {{
            flex: 1;
            max-width: 320px;
            position: relative;
        }}
        .header-search input {{
            width: 100%;
            background: var(--panel-2);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 7px 12px;
            border-radius: 4px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12px;
        }}
        .ticker-pills {{ display: flex; gap: 6px; overflow: hidden; }}
        .pill {{
            background: var(--panel-2);
            border: 1px solid var(--border);
            padding: 4px 8px;
            border-radius: 3px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
            cursor: pointer;
        }}
        .pill:hover {{ border-color: var(--accent); }}
        .header-meta {{ margin-left: auto; text-align: right; font-size: 11px; color: var(--text-dim); }}
        .header-status {{ display: flex; align-items: center; gap: 6px; color: var(--up); font-size: 11px; }}
        .status-dot {{ width: 7px; height: 7px; border-radius: 50%; background: var(--up); box-shadow: 0 0 6px var(--up); }}
        .disclaimer {{ color: var(--text-dim); font-size: 10px; }}

        /* Ticker tape */
        .tape-container {{
            height: 32px;
            background: #0a0e13;
            border-bottom: 1px solid var(--border);
            overflow: hidden;
            display: flex;
            align-items: center;
            flex-shrink: 0;
        }}
        .tape {{
            display: flex;
            gap: 28px;
            white-space: nowrap;
            animation: tape-scroll 60s linear infinite;
            padding-left: 100%;
        }}
        @keyframes tape-scroll {{
            0% {{ transform: translateX(0); }}
            100% {{ transform: translateX(-100%); }}
        }}
        .tape-item {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12px;
        }}
        .t-ticker {{ font-weight: 600; color: var(--text); }}
        .t-name {{ color: var(--text-dim); }}
        .t-price {{ font-weight: 600; }}
        .t-pct {{ font-weight: 600; }}

        /* Main layout */
        .main-layout {{
            display: flex;
            flex: 1;
            min-height: 0;
            overflow: hidden;
        }}
        .left-rail {{
            width: 210px;
            background: var(--panel);
            border-right: 1px solid var(--border);
            overflow-y: auto;
            flex-shrink: 0;
        }}
        .rail-header {{
            padding: 12px;
            border-bottom: 1px solid var(--border);
            font-weight: 600;
            font-size: 12px;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .wl-group {{ border-bottom: 1px solid var(--border); }}
        .wl-group-title {{
            padding: 8px 12px;
            background: var(--panel-2);
            color: var(--text-dim);
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }}
        .wl-item {{
            padding: 10px 12px;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: background 0.15s;
        }}
        .wl-item:hover, .wl-item.active {{ background: #192436; }}
        .wl-ticker {{ font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 13px; }}
        .wl-name {{ color: var(--text-dim); font-size: 10px; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .wl-meta {{ display: flex; justify-content: space-between; margin-top: 4px; font-family: 'IBM Plex Mono', monospace; font-size: 11px; }}

        .center-workspace {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            background: var(--bg);
        }}
        .tab-bar {{
            display: flex;
            background: var(--panel);
            border-bottom: 1px solid var(--border);
            flex-shrink: 0;
        }}
        .tab {{
            padding: 10px 16px;
            cursor: pointer;
            border-right: 1px solid var(--border);
            color: var(--text-dim);
            font-size: 12px;
            font-weight: 500;
            white-space: nowrap;
        }}
        .tab:hover {{ color: var(--text); background: #17202b; }}
        .tab.active {{ color: var(--text); background: var(--bg); border-bottom: 2px solid var(--accent); }}

        .tab-content {{
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: none;
        }}
        .tab-content.active {{ display: block; }}

        .right-panel {{
            width: 300px;
            background: var(--panel);
            border-left: 1px solid var(--border);
            overflow-y: auto;
            flex-shrink: 0;
        }}
        .panel-section {{ border-bottom: 1px solid var(--border); }}
        .panel-section-title {{
            padding: 12px;
            font-weight: 600;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--accent);
        }}
        .note {{
            padding: 10px 12px;
            border-bottom: 1px solid var(--border);
            font-size: 11px;
            line-height: 1.45;
        }}
        .note-ticker {{ font-family: 'IBM Plex Mono', monospace; font-weight: 600; margin-right: 6px; }}
        .note-agreement {{ border-left: 3px solid var(--agree); }}
        .note-divergence {{ border-left: 3px solid var(--diverge); }}
        .note-risk {{ border-left: 3px solid var(--risk); }}
        .note-watch {{ border-left: 3px solid var(--accent-2); }}

        /* Content cards */
        .section-title {{
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 12px;
            color: var(--text);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .card {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 6px;
            margin-bottom: 16px;
            overflow: hidden;
        }}
        .card-header {{
            padding: 10px 12px;
            border-bottom: 1px solid var(--border);
            font-weight: 600;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .card-body {{ padding: 12px; }}
        .chart-container {{
            width: 100%;
            height: 360px;
            min-height: 300px;
        }}
        .chart-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
            gap: 16px;
        }}
        .chart-sm {{ height: 220px; }}
        .chart-expand {{
            font-size: 11px;
            color: var(--text-dim);
            cursor: pointer;
        }}
        .chart-expand:hover {{ color: var(--accent); }}

        /* Tables */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }}
        .data-table th, .data-table td {{
            padding: 8px 10px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        .data-table th {{
            background: var(--panel-2);
            color: var(--text-dim);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 10px;
            letter-spacing: 0.3px;
            position: sticky;
            top: 0;
        }}
        .data-table tr:hover {{ background: #17202b; }}
        .data-table td {{ font-family: 'IBM Plex Mono', monospace; }}

        /* News */
        .news-card {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 12px;
            margin-bottom: 10px;
        }}
        .news-header {{ display: flex; gap: 8px; align-items: center; margin-bottom: 6px; flex-wrap: wrap; }}
        .news-ticker {{ font-family: 'IBM Plex Mono', monospace; font-weight: 600; color: var(--accent); }}
        .news-date {{ color: var(--text-dim); font-size: 11px; }}
        .news-badge {{ font-size: 9px; padding: 2px 5px; border-radius: 3px; font-weight: 600; }}
        .news-badge.recent {{ background: #1a3a22; color: var(--up); }}
        .news-badge.background {{ background: #3a2a1a; color: var(--warn); }}
        .news-title {{ font-weight: 600; font-size: 12px; margin-bottom: 4px; }}
        .news-source {{ font-size: 10px; color: var(--text-dim); word-break: break-all; }}
        .news-why {{ font-size: 11px; color: var(--text-dim); margin-top: 6px; }}

        /* Badges */
        .badge-selected {{ background: #1a3a22; color: var(--up); padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: 600; }}
        .badge-excluded {{ background: #3a1a1a; color: var(--down); padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: 600; }}

        /* Bottom drawer */
        .bottom-drawer {{
            height: 28px;
            background: var(--panel);
            border-top: 1px solid var(--border);
            flex-shrink: 0;
            overflow: hidden;
            transition: height 0.25s ease;
            z-index: 50;
        }}
        .bottom-drawer.open {{ height: 260px; }}
        .drawer-bar {{
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            cursor: pointer;
            font-size: 11px;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .drawer-content {{
            height: calc(100% - 28px);
            overflow-y: auto;
            padding: 12px 16px;
            display: none;
        }}
        .bottom-drawer.open .drawer-content {{ display: block; }}
        .drawer-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }}
        .drawer-section-title {{ color: var(--accent); font-weight: 600; font-size: 11px; margin-bottom: 6px; text-transform: uppercase; }}
        .drawer-section ul {{ margin: 0; padding-left: 16px; color: var(--text-dim); font-size: 11px; line-height: 1.6; }}
        .drawer-section p {{ color: var(--text-dim); font-size: 11px; line-height: 1.5; margin: 0; }}

        /* Modal */
        .modal-overlay {{
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.8);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }}
        .modal-overlay.open {{ display: flex; }}
        .modal-box {{
            width: 90vw;
            height: 80vh;
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 8px;
            display: flex;
            flex-direction: column;
        }}
        .modal-header {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .modal-close {{ cursor: pointer; color: var(--text-dim); font-size: 18px; }}
        .modal-close:hover {{ color: var(--text); }}
        .modal-chart {{ flex: 1; padding: 12px; }}

        /* Sparkline grid */
        .spark-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
        }}
        .spark-box {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 10px;
        }}
        .spark-title {{ font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 12px; margin-bottom: 4px; }}
        .spark-sub {{ color: var(--text-dim); font-size: 10px; margin-bottom: 8px; }}
        .spark-chart {{ height: 70px; }}

        /* Responsive */
        @media (max-width: 1100px) {{
            .left-rail {{ display: none; }}
            .right-panel {{ width: 260px; }}
        }}
        @media (max-width: 900px) {{
            .right-panel {{ display: none; }}
        }}
    </style>
</head>
<body>
    <header class="terminal-header">
        <div>
            <div class="terminal-title">⚡ CLEAN ENERGY & POWER INFRASTRUCTURE</div>
            <div class="terminal-subtitle">U.S. Equity Research Workbench</div>
        </div>
        <div class="header-search">
            <input type="text" id="global-search" placeholder="Search ticker, company, segment..." onkeyup="handleSearch(event)">
        </div>
        <div class="ticker-pills" id="header-pills"></div>
        <div class="header-meta">
            <div class="header-status"><span class="status-dot"></span> LIVE DATA | {REPORT_TS}</div>
            <div class="disclaimer">For research only. Not investment advice.</div>
        </div>
    </header>

    <div class="tape-container">
        <div class="tape" id="tape">
            {tape_items_html}
            {tape_items_html}
        </div>
    </div>

    <div class="main-layout">
        <aside class="left-rail">
            <div class="rail-header">Watchlist</div>
            {watchlist_html}
        </aside>

        <main class="center-workspace">
            <nav class="tab-bar">
                <div class="tab active" data-tab="snapshot" onclick="switchTab('snapshot')">Market Snapshot</div>
                <div class="tab" data-tab="peer" onclick="switchTab('peer')">Peer Comparison</div>
                <div class="tab" data-tab="candles" onclick="switchTab('candles')">Candlestick Charts</div>
                <div class="tab" data-tab="financials" onclick="switchTab('financials')">Financial Deep-Dive</div>
                <div class="tab" data-tab="signals" onclick="switchTab('signals')">Theme Signals</div>
                <div class="tab" data-tab="evidence" onclick="switchTab('evidence')">Evidence Feed</div>
                <div class="tab" data-tab="valuation" onclick="switchTab('valuation')">Valuation Context</div>
            </nav>

            <!-- Market Snapshot -->
            <section class="tab-content active" id="tab-snapshot">
                <div class="card">
                    <div class="card-header">
                        <span>Market Snapshot — Selected Universe</span>
                        <span class="chart-expand" onclick="expandChart('snapshot-spark')">Expand</span>
                    </div>
                    <div class="card-body">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Ticker</th>
                                    <th>Company</th>
                                    <th>Segment</th>
                                    <th>Price</th>
                                    <th>1D Chg</th>
                                    <th>Mkt Cap</th>
                                    <th>Trailing P/E</th>
                                    <th>Forward P/E</th>
                                    <th>Beta</th>
                                    <th>Div Yield</th>
                                    <th>Revenue TTM</th>
                                </tr>
                            </thead>
                            <tbody>
                                {snapshot_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><span>Performance Sparklines (6M)</span></div>
                    <div class="card-body">
                        <div class="spark-grid" id="snapshot-spark-grid"></div>
                    </div>
                </div>
            </section>

            <!-- Peer Comparison -->
            <section class="tab-content" id="tab-peer">
                <div class="card">
                    <div class="card-header"><span>Peer Comparison Matrix</span></div>
                    <div class="card-body" style="overflow-x:auto;">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Ticker</th>
                                    <th>Mkt Cap</th>
                                    <th>Trail P/E</th>
                                    <th>Fwd P/E</th>
                                    <th>EV/EBITDA</th>
                                    <th>P/S</th>
                                    <th>P/B</th>
                                    <th>Gross Mgn</th>
                                    <th>Net Mgn</th>
                                    <th>Rev TTM</th>
                                    <th>Op CF</th>
                                    <th>FCF</th>
                                    <th>Debt</th>
                                    <th>Quick</th>
                                </tr>
                            </thead>
                            <tbody>{peer_rows}</tbody>
                        </table>
                    </div>
                </div>
                <div class="chart-row">
                    <div class="card">
                        <div class="card-header"><span>Market Cap Comparison</span></div>
                        <div class="card-body"><div id="chart-mktcap" class="chart-container chart-sm"></div></div>
                    </div>
                    <div class="card">
                        <div class="card-header"><span>Revenue TTM Comparison</span></div>
                        <div class="card-body"><div id="chart-revenue" class="chart-container chart-sm"></div></div>
                    </div>
                </div>
            </section>

            <!-- Candlestick Charts -->
            <section class="tab-content" id="tab-candles">
                <div class="card">
                    <div class="card-header"><span>Candlestick / OHLC Dashboard — Representative Names</span></div>
                    <div class="card-body">
                        <p style="color:var(--text-dim);font-size:11px;margin-bottom:12px;">
                            Charts rendered from embedded <code>market_ohlcv.json</code> with volume and 5/10/20-day moving averages where data supports.
                        </p>
                        <div id="chart-candle-main" class="chart-container" style="height:520px;"></div>
                    </div>
                </div>
                <div class="chart-row">
                    {"".join(f'''<div class="card"><div class="card-header"><span>{t} — OHLC</span></div><div class="card-body"><div id="chart-candle-{t}" class="chart-container chart-sm"></div></div></div>''' for t in json.loads(cand_json))}
                </div>
            </section>

            <!-- Financial Deep-Dive -->
            <section class="tab-content" id="tab-financials">
                <div class="chart-row">
                    <div class="card">
                        <div class="card-header"><span>Gross Margin vs Net Margin</span></div>
                        <div class="card-body"><div id="chart-margins" class="chart-container"></div></div>
                    </div>
                    <div class="card">
                        <div class="card-header"><span>Cash Flow, Capex & FCF</span></div>
                        <div class="card-body"><div id="chart-cashflow" class="chart-container"></div></div>
                    </div>
                </div>
                <div class="chart-row">
                    <div class="card">
                        <div class="card-header"><span>Balance Sheet Risk — Debt vs Cash</span></div>
                        <div class="card-body"><div id="chart-debt" class="chart-container"></div></div>
                    </div>
                    <div class="card">
                        <div class="card-header"><span>Working Capital Risk — Inventory & Receivables</span></div>
                        <div class="card-body"><div id="chart-wc" class="chart-container"></div></div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><span>Annual Revenue Trend</span></div>
                    <div class="card-body"><div id="chart-rev-trend" class="chart-container"></div></div>
                </div>
            </section>

            <!-- Theme Signals -->
            <section class="tab-content" id="tab-signals">
                <div class="chart-row">
                    <div class="card">
                        <div class="card-header"><span>Theme Exposure Distribution</span></div>
                        <div class="card-body"><div id="chart-segment" class="chart-container chart-sm"></div></div>
                    </div>
                    <div class="card">
                        <div class="card-header"><span>Evidence Strength / Data Completeness Matrix</span></div>
                        <div class="card-body"><div id="chart-completeness" class="chart-container chart-sm"></div></div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><span>Theme Signal Summary</span></div>
                    <div class="card-body">
                        <ul style="color:var(--text-dim);line-height:1.7;font-size:12px;">
                            <li><strong>Data-center power demand</strong> is a cross-cutting catalyst for utilities (NEE, VST, NRG, AES), grid builders (PWR), and power-equipment suppliers (GEV, ETN).</li>
                            <li><strong>Solar + storage</strong> remains represented by ENPH (microinverters/batteries) and NXT (tracking); module manufacturers were ranked lower in composite scoring but remain on the watchlist.</li>
                            <li><strong>Nuclear / clean baseload</strong> exposure is concentrated in CEG (Constellation Energy), which has outperformed on AI/data-center power demand.</li>
                            <li><strong>Battery/EV materials</strong> exposure comes through TSLA (vertical integration) rather than raw-material names, which screen lower on near-term data quality.</li>
                            <li>Valuation dispersion is wide: forward P/E ranges from low double-digits to &gt;40x, indicating the market is pricing divergent earnings trajectories.</li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- Evidence Feed -->
            <section class="tab-content" id="tab-evidence">
                <div class="card">
                    <div class="card-header"><span>Recent News & Catalysts (Last 30 Days)</span></div>
                    <div class="card-body">
                        {recent_news_html if recent_news_html else '<p style="color:var(--text-dim)">No recent items returned by data source.</p>'}
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><span>Background Context (Older Items)</span></div>
                    <div class="card-body">
                        {bg_news_html if bg_news_html else '<p style="color:var(--text-dim)">No background items returned by data source.</p>'}
                    </div>
                </div>
            </section>

            <!-- Valuation Context -->
            <section class="tab-content" id="tab-valuation">
                <div class="chart-row">
                    <div class="card">
                        <div class="card-header"><span>Valuation Multiples — P/E & EV/EBITDA</span></div>
                        <div class="card-body"><div id="chart-val-multiples" class="chart-container"></div></div>
                    </div>
                    <div class="card">
                        <div class="card-header"><span>Price Performance Comparison (6M)</span></div>
                        <div class="card-body"><div id="chart-performance" class="chart-container"></div></div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><span>Valuation Context Table</span></div>
                    <div class="card-body" style="overflow-x:auto;">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Ticker</th>
                                    <th>Price</th>
                                    <th>Target Price</th>
                                    <th>Upside / (Downside)</th>
                                    <th>Trail P/E</th>
                                    <th>Fwd P/E</th>
                                    <th>EV/EBITDA</th>
                                    <th>P/B</th>
                                    <th>Analyst Rec</th>
                                    <th>Short % Float</th>
                                </tr>
                            </thead>
                            <tbody>
                                {"".join(valuation_row(t, companies[t]) for t in tickers)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>
        </main>

        <aside class="right-panel">
            <div class="panel-section">
                <div class="panel-section-title">Agreement Signals</div>
                {"".join(note_html(n) for n in analyst_notes if n['type'] == 'agreement')}
                {"<div class='note' style='color:var(--text-dim)'>No strong agreement signals.</div>" if not any(n['type'] == 'agreement' for n in analyst_notes) else ""}
            </div>
            <div class="panel-section">
                <div class="panel-section-title">Divergence Signals</div>
                {"".join(note_html(n) for n in analyst_notes if n['type'] == 'divergence')}
                {"<div class='note' style='color:var(--text-dim)'>No divergence flags.</div>" if not any(n['type'] == 'divergence' for n in analyst_notes) else ""}
            </div>
            <div class="panel-section">
                <div class="panel-section-title">Risk Flags</div>
                {"".join(note_html(n) for n in analyst_notes if n['type'] == 'risk')}
                {"<div class='note' style='color:var(--text-dim)'>No risk flags triggered.</div>" if not any(n['type'] == 'risk' for n in analyst_notes) else ""}
            </div>
            <div class="panel-section">
                <div class="panel-section-title">Watch Items</div>
                {"".join(note_html(n) for n in analyst_notes if n['type'] == 'watch')}
            </div>
            <div class="panel-section">
                <div class="panel-section-title">Research Actions</div>
                <div class="note note-watch">
                    <span class="note-ticker">ALL</span>
                    <span class="note-text">Monitor 2Q26 earnings and data-center power demand commentary; track IRA/policy tailwinds; watch interest-rate sensitivity.</span>
                </div>
            </div>
        </aside>
    </div>

    <div class="bottom-drawer" id="drawer">
        <div class="drawer-bar" onclick="toggleDrawer()">
            <span>▼ Source Inventory / Audit Trail / Data Limitations</span>
            <span>Click to expand</span>
        </div>
        <div class="drawer-content">
            <div class="drawer-grid">
                <div class="drawer-section">
                    <div class="drawer-section-title">Source Inventory</div>
                    <ul>
                        <li><strong>Market data & OHLCV:</strong> Yahoo Finance via yfinance — saved to <code>market_ohlcv.json</code>.</li>
                        <li><strong>Company profiles & fundamentals:</strong> Yahoo Finance quote pages and financial statements.</li>
                        <li><strong>News:</strong> Yahoo Finance news stream per ticker.</li>
                        <li><strong>Selection methodology:</strong> Internal composite scoring (relevance, data completeness, market cap, analyst coverage).</li>
                    </ul>
                </div>
                <div class="drawer-section">
                    <div class="drawer-section-title">Local File Paths</div>
                    <ul>
                        <li><code>us_clean_energy_power_research_workbench/research_workbench.html</code></li>
                        <li><code>us_clean_energy_power_research_workbench/us_clean_energy_power_peer_comps.xlsx</code></li>
                        <li><code>us_clean_energy_power_research_workbench/source_inventory.xlsx</code></li>
                        <li><code>us_clean_energy_power_research_workbench/market_ohlcv.json</code></li>
                        <li><code>us_clean_energy_power_research_workbench/raw/candidate_screen.json</code></li>
                        <li><code>us_clean_energy_power_research_workbench/raw/final_company_data.json</code></li>
                        <li><code>us_clean_energy_power_research_workbench/raw/news_feed.json</code></li>
                    </ul>
                </div>
                <div class="drawer-section">
                    <div class="drawer-section-title">Data Limitations</div>
                    <ul>
                        <li>All values are sourced from Yahoo Finance; gaps marked as null/blank.</li>
                        <li>Financial statement extracts use the most recent annual reports available; quarterly items approximate TTM.</li>
                        <li>News coverage depends on Yahoo's aggregation and may omit paywalled sources.</li>
                        <li>Prices are adjusted for splits/dividends; intraday data is not used.</li>
                    </ul>
                </div>
                <div class="drawer-section">
                    <div class="drawer-section-title">Audit Trail</div>
                    <p>Report generated: <strong>{REPORT_TS}</strong></p>
                    <p>Reference pool: {len(screen["reference_pool"])} tickers</p>
                    <p>Final selections: {len(tickers)} tickers — {', '.join(tickers)}</p>
                    <p>Data provider: Yahoo Finance via yfinance (Python)</p>
                </div>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="modal" onclick="closeModal(event)">
        <div class="modal-box" onclick="event.stopPropagation()">
            <div class="modal-header">
                <span id="modal-title">Chart</span>
                <span class="modal-close" onclick="closeModal()">×</span>
            </div>
            <div class="modal-chart" id="modal-chart"></div>
        </div>
    </div>

    <!-- Embedded data -->
    <script type="application/json" id="market-ohlcv-data">{ohlcv_json}</script>
    <script type="application/json" id="company-data">{final_json}</script>
    <script type="application/json" id="news-data">{news_json}</script>
    <script type="application/json" id="screen-data">{screen_json}</script>
    <script type="application/json" id="tape-data">{tape_json}</script>
    <script type="application/json" id="segments-data">{segments_json}</script>
    <script type="application/json" id="candle-tickers">{cand_json}</script>

    <script>
        // Data parsing
        const ohlcvData = JSON.parse(document.getElementById('market-ohlcv-data').textContent);
        const companyData = JSON.parse(document.getElementById('company-data').textContent);
        const newsData = JSON.parse(document.getElementById('news-data').textContent);
        const screenData = JSON.parse(document.getElementById('screen-data').textContent);
        const tapeData = JSON.parse(document.getElementById('tape-data').textContent);
        const segmentsData = JSON.parse(document.getElementById('segments-data').textContent);
        const candleTickers = JSON.parse(document.getElementById('candle-tickers').textContent);
        const tickers = companyData.tickers;
        const companies = companyData.companies;

        // Populate header pills
        document.getElementById('header-pills').innerHTML = tickers.map(t =>
            `<span class="pill" onclick="focusTicker('${{t}}')">${{t}}</span>`
        ).join('');

        const chartInstances = {{}};
        let modalChart = null;

        // Helpers
        function formatPct(v) {{ return v == null ? 'N/A' : (v >= 0 ? '+' : '') + (v*100).toFixed(2) + '%'; }}
        function formatB(v) {{ return v == null ? 'N/A' : '$' + (v/1e9).toFixed(2) + 'B'; }}
        function colorByVal(v) {{ return (v == null || v >= 0) ? '#22c55e' : '#ef4444'; }}

        // Tab switching
        function switchTab(id) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + id).classList.add('active');
            document.querySelector('.tab[data-tab="' + id + '"]').classList.add('active');
            // Resize charts in active tab
            setTimeout(() => {{ Object.values(chartInstances).forEach(c => c && c.resize()); }}, 50);
        }}

        function toggleDrawer() {{
            document.getElementById('drawer').classList.toggle('open');
        }}

        function focusTicker(ticker) {{
            document.querySelectorAll('.wl-item').forEach(el => el.classList.remove('active'));
            const el = document.querySelector('.wl-item[data-ticker="' + ticker + '"]');
            if (el) el.classList.add('active');
            // Could scroll candles tab to ticker chart in future
        }}

        function handleSearch(e) {{
            const q = e.target.value.toLowerCase();
            document.querySelectorAll('.wl-item').forEach(el => {{
                const txt = el.textContent.toLowerCase();
                el.style.display = txt.includes(q) ? 'block' : 'none';
            }});
        }}

        function openModal(title, option) {{
            document.getElementById('modal-title').textContent = title;
            document.getElementById('modal').classList.add('open');
            if (modalChart) modalChart.dispose();
            modalChart = echarts.init(document.getElementById('modal-chart'));
            modalChart.setOption(option);
        }}

        function closeModal(e) {{
            if (e && e.target !== document.getElementById('modal')) return;
            document.getElementById('modal').classList.remove('open');
            if (modalChart) {{ modalChart.dispose(); modalChart = null; }}
        }}

        function ma(data, period) {{
            return data.map((_, i, arr) => {{
                if (i < period - 1) return null;
                const sum = arr.slice(i - period + 1, i + 1).reduce((a, b) => a + b.close, 0);
                return sum / period;
            }});
        }}

        function buildCandleOption(record, showVolume) {{
            const dates = record.bars.map(b => b.date);
            const values = record.bars.map(b => [b.open, b.close, b.low, b.high]);
            const volumes = record.bars.map(b => b.volume);
            const closes = record.bars.map(b => b.close);
            const ma5 = ma(record.bars, 5);
            const ma10 = ma(record.bars, 10);
            const ma20 = ma(record.bars, 20);
            const series = [
                {{ type: 'candlestick', name: record.ticker, data: values, itemStyle: {{ color: '#22c55e', color0: '#ef4444', borderColor: '#22c55e', borderColor0: '#ef4444' }} }},
                {{ type: 'line', name: 'MA5', data: ma5, smooth: true, showSymbol: false, lineStyle: {{ width: 1, color: '#f59e0b' }} }},
                {{ type: 'line', name: 'MA10', data: ma10, smooth: true, showSymbol: false, lineStyle: {{ width: 1, color: '#38bdf8' }} }},
                {{ type: 'line', name: 'MA20', data: ma20, smooth: true, showSymbol: false, lineStyle: {{ width: 1, color: '#a78bfa' }} }}
            ];
            const grid = showVolume ? [
                {{ left: 50, right: 20, top: 30, height: '55%' }},
                {{ left: 50, right: 20, top: '68%', height: '20%' }}
            ] : [{{ left: 50, right: 20, top: 30, bottom: 40 }}];
            const xAxis = showVolume ? [
                {{ type: 'category', data: dates, scale: true, boundaryGap: false, axisLine: {{ lineStyle: {{ color: '#334155' }} }}, axisLabel: {{ color: '#8b9aae' }} }},
                {{ type: 'category', data: dates, gridIndex: 1, scale: true, boundaryGap: false, axisLine: {{ lineStyle: {{ color: '#334155' }} }}, axisLabel: {{ show: false }} }}
            ] : [{{ type: 'category', data: dates, scale: true, boundaryGap: false, axisLine: {{ lineStyle: {{ color: '#334155' }} }}, axisLabel: {{ color: '#8b9aae', rotate: 30 }} }}];
            const yAxis = showVolume ? [
                {{ scale: true, gridIndex: 0, splitLine: {{ lineStyle: {{ color: '#1f2a38' }} }}, axisLabel: {{ color: '#8b9aae' }} }},
                {{ scale: true, gridIndex: 1, splitNumber: 2, axisLabel: {{ show: false }}, axisLine: {{ show: false }}, splitLine: {{ show: false }} }}
            ] : [{{ scale: true, splitLine: {{ lineStyle: {{ color: '#1f2a38' }} }}, axisLabel: {{ color: '#8b9aae' }} }}];

            const option = {{
                backgroundColor: 'transparent',
                tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'cross' }}, backgroundColor: '#111821', borderColor: '#1f2a38', textStyle: {{ color: '#e6edf3' }} }},
                legend: {{ data: [record.ticker, 'MA5', 'MA10', 'MA20'], textStyle: {{ color: '#8b9aae' }}, top: 0 }},
                grid: grid,
                xAxis: xAxis,
                yAxis: yAxis,
                series: series
            }};
            if (showVolume) {{
                option.series.push({{
                    type: 'bar', name: 'Volume', xAxisIndex: 1, yAxisIndex: 1, data: volumes,
                    itemStyle: {{ color: (params) => params.value >= 0 ? '#22c55e' : '#ef4444' }}
                }});
                option.legend.data.push('Volume');
            }}
            return option;
        }}

        // Render candlestick charts
        function renderCandles() {{
            const mainContainer = document.getElementById('chart-candle-main');
            if (mainContainer) {{
                const mainChart = echarts.init(mainContainer);
                const series = [];
                const legend = [];
                candleTickers.forEach(t => {{
                    const rec = ohlcvData.records.find(r => r.ticker === t);
                    if (!rec) return;
                    const closes = rec.bars.map(b => b.close);
                    const base = closes[0];
                    const normalized = closes.map(v => ((v - base) / base) * 100);
                    series.push({{ type: 'line', name: t, data: normalized, smooth: false, showSymbol: false, lineStyle: {{ width: 1.5 }} }});
                    legend.push(t);
                }});
                mainChart.setOption({{
                    backgroundColor: 'transparent',
                    title: {{ text: 'Normalized Price Performance (%) — Representative Names', left: 0, textStyle: {{ color: '#e6edf3', fontSize: 13 }} }},
                    tooltip: {{ trigger: 'axis', backgroundColor: '#111821', borderColor: '#1f2a38', textStyle: {{ color: '#e6edf3' }} }},
                    legend: {{ data: legend, textStyle: {{ color: '#8b9aae' }}, top: 22 }},
                    grid: {{ left: 50, right: 20, top: 55, bottom: 40 }},
                    xAxis: {{ type: 'category', data: ohlcvData.records[0].bars.map(b => b.date), axisLine: {{ lineStyle: {{ color: '#334155' }} }}, axisLabel: {{ color: '#8b9aae', rotate: 30 }} }},
                    yAxis: {{ scale: true, splitLine: {{ lineStyle: {{ color: '#1f2a38' }} }}, axisLabel: {{ color: '#8b9aae', formatter: '{{value}}%' }} }},
                    series: series,
                    dataZoom: [{{ type: 'inside' }}, {{ type: 'slider', bottom: 5 }}]
                }});
                chartInstances['candle-main'] = mainChart;
            }}

            candleTickers.forEach(t => {{
                const container = document.getElementById('chart-candle-' + t);
                if (!container) return;
                const rec = ohlcvData.records.find(r => r.ticker === t);
                if (!rec) return;
                const chart = echarts.init(container);
                const option = buildCandleOption(rec, false);
                chart.setOption(option);
                chartInstances['candle-' + t] = chart;
                chart.on('dblclick', () => openModal(t + ' — OHLC', option));
            }});
        }}

        // Sparklines
        function renderSparklines() {{
            const grid = document.getElementById('snapshot-spark-grid');
            if (!grid) return;
            tickers.forEach(t => {{
                const rec = ohlcvData.records.find(r => r.ticker === t);
                if (!rec) return;
                const box = document.createElement('div');
                box.className = 'spark-box';
                const last6m = rec.bars.slice(-126);
                const closes = last6m.map(b => b.close);
                const base = closes[0];
                const perf = ((closes[closes.length - 1] - base) / base) * 100;
                const color = perf >= 0 ? '#22c55e' : '#ef4444';
                box.innerHTML = `
                    <div class="spark-title">${{t}}</div>
                    <div class="spark-sub">6M: <span style="color:${{color}}">${{perf >= 0 ? '+' : ''}}${{perf.toFixed(2)}}%</span></div>
                    <div class="spark-chart" id="spark-${{t}}"></div>
                `;
                grid.appendChild(box);
                const chart = echarts.init(document.getElementById('spark-' + t));
                chart.setOption({{
                    backgroundColor: 'transparent',
                    grid: {{ left: 0, right: 0, top: 2, bottom: 2 }},
                    xAxis: {{ type: 'category', data: last6m.map(b => b.date), show: false }},
                    yAxis: {{ type: 'value', show: false, scale: true }},
                    series: [{{ type: 'line', data: closes, showSymbol: false, lineStyle: {{ width: 1.5, color: color }}, areaStyle: {{ color: new echarts.graphic.LinearGradient(0,0,0,1, [{{offset:0, color: color+'44'}}, {{offset:1, color: color+'00'}}]) }} }}]
                }});
                chartInstances['spark-' + t] = chart;
            }});
        }}

        // Bar charts
        function renderBarChart(id, title, data, color) {{
            const container = document.getElementById(id);
            if (!container) return;
            const chart = echarts.init(container);
            chart.setOption({{
                backgroundColor: 'transparent',
                title: {{ text: title, left: 0, textStyle: {{ color: '#e6edf3', fontSize: 12 }} }},
                tooltip: {{ trigger: 'axis', backgroundColor: '#111821', borderColor: '#1f2a38', textStyle: {{ color: '#e6edf3' }} }},
                grid: {{ left: 50, right: 10, top: 35, bottom: 25 }},
                xAxis: {{ type: 'category', data: data.map(d => d.name), axisLine: {{ lineStyle: {{ color: '#334155' }} }}, axisLabel: {{ color: '#8b9aae', interval: 0, rotate: 30 }} }},
                yAxis: {{ type: 'value', splitLine: {{ lineStyle: {{ color: '#1f2a38' }} }}, axisLabel: {{ color: '#8b9aae' }} }},
                series: [{{ type: 'bar', data: data.map(d => d.value), itemStyle: {{ color: color || '#38bdf8' }} }}]
            }});
            chartInstances[id] = chart;
        }}

        function renderGroupedBarChart(id, title, legends, categories, seriesData) {{
            const container = document.getElementById(id);
            if (!container) return;
            const chart = echarts.init(container);
            chart.setOption({{
                backgroundColor: 'transparent',
                title: {{ text: title, left: 0, textStyle: {{ color: '#e6edf3', fontSize: 12 }} }},
                tooltip: {{ trigger: 'axis', backgroundColor: '#111821', borderColor: '#1f2a38', textStyle: {{ color: '#e6edf3' }} }},
                legend: {{ data: legends, textStyle: {{ color: '#8b9aae' }}, top: 20 }},
                grid: {{ left: 50, right: 10, top: 50, bottom: 25 }},
                xAxis: {{ type: 'category', data: categories, axisLine: {{ lineStyle: {{ color: '#334155' }} }}, axisLabel: {{ color: '#8b9aae', interval: 0, rotate: 30 }} }},
                yAxis: {{ type: 'value', splitLine: {{ lineStyle: {{ color: '#1f2a38' }} }}, axisLabel: {{ color: '#8b9aae' }} }},
                series: seriesData
            }});
            chartInstances[id] = chart;
        }}

        function renderLineChart(id, title, xData, series) {{
            const container = document.getElementById(id);
            if (!container) return;
            const chart = echarts.init(container);
            chart.setOption({{
                backgroundColor: 'transparent',
                title: {{ text: title, left: 0, textStyle: {{ color: '#e6edf3', fontSize: 12 }} }},
                tooltip: {{ trigger: 'axis', backgroundColor: '#111821', borderColor: '#1f2a38', textStyle: {{ color: '#e6edf3' }} }},
                legend: {{ data: series.map(s => s.name), textStyle: {{ color: '#8b9aae' }}, top: 20 }},
                grid: {{ left: 50, right: 10, top: 50, bottom: 35 }},
                xAxis: {{ type: 'category', data: xData, axisLine: {{ lineStyle: {{ color: '#334155' }} }}, axisLabel: {{ color: '#8b9aae', rotate: 30 }} }},
                yAxis: {{ type: 'value', splitLine: {{ lineStyle: {{ color: '#1f2a38' }} }}, axisLabel: {{ color: '#8b9aae' }} }},
                series: series
            }});
            chartInstances[id] = chart;
        }}

        function renderPieChart(id, title, data) {{
            const container = document.getElementById(id);
            if (!container) return;
            const chart = echarts.init(container);
            chart.setOption({{
                backgroundColor: 'transparent',
                title: {{ text: title, left: 'center', textStyle: {{ color: '#e6edf3', fontSize: 12 }} }},
                tooltip: {{ trigger: 'item', backgroundColor: '#111821', borderColor: '#1f2a38', textStyle: {{ color: '#e6edf3' }} }},
                legend: {{ orient: 'vertical', left: 'left', textStyle: {{ color: '#8b9aae' }} }},
                series: [{{ type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: false, label: {{ color: '#8b9aae' }}, data: data }}]
            }});
            chartInstances[id] = chart;
        }}

        function renderHeatmap(id, title, xData, yData, data) {{
            const container = document.getElementById(id);
            if (!container) return;
            const chart = echarts.init(container);
            chart.setOption({{
                backgroundColor: 'transparent',
                title: {{ text: title, left: 0, textStyle: {{ color: '#e6edf3', fontSize: 12 }} }},
                tooltip: {{ position: 'top', backgroundColor: '#111821', borderColor: '#1f2a38', textStyle: {{ color: '#e6edf3' }} }},
                grid: {{ left: 80, right: 20, top: 30, bottom: 40 }},
                xAxis: {{ type: 'category', data: xData, splitArea: {{ show: true }}, axisLabel: {{ color: '#8b9aae' }} }},
                yAxis: {{ type: 'category', data: yData, splitArea: {{ show: true }}, axisLabel: {{ color: '#8b9aae' }} }},
                visualMap: {{ min: 0, max: 1, calculable: true, orient: 'horizontal', left: 'center', bottom: 0, inRange: {{ color: ['#1f2a38', '#38bdf8'] }}, textStyle: {{ color: '#8b9aae' }} }},
                series: [{{ name: 'Completeness', type: 'heatmap', data: data, label: {{ show: true, color: '#e6edf3' }}, emphasis: {{ itemStyle: {{ shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' }} }} }}]
            }});
            chartInstances[id] = chart;
        }}

        function initCharts() {{
            renderSparklines();
            renderCandles();

            // Market cap
            renderBarChart('chart-mktcap', '', tickers.map(t => ({{ name: t, value: companies[t].market.market_cap || 0 }})), '#38bdf8');

            // Revenue TTM
            renderBarChart('chart-revenue', '', tickers.map(t => ({{ name: t, value: companies[t].financials.revenue_ttm || 0 }})), '#22c55e');

            // Margins
            renderGroupedBarChart('chart-margins', '',
                ['Gross Margin %', 'Net Margin %'],
                tickers,
                [
                    {{ name: 'Gross Margin %', type: 'bar', data: tickers.map(t => companies[t].financials.gross_margin == null ? 0 : companies[t].financials.gross_margin * 100), itemStyle: {{ color: '#22c55e' }} }},
                    {{ name: 'Net Margin %', type: 'bar', data: tickers.map(t => companies[t].financials.net_margin == null ? 0 : companies[t].financials.net_margin * 100), itemStyle: {{ color: '#f59e0b' }} }}
                ]
            );

            // Cash flow
            renderGroupedBarChart('chart-cashflow', '',
                ['Operating CF', 'Capex', 'FCF'],
                tickers,
                [
                    {{ name: 'Operating CF', type: 'bar', data: tickers.map(t => companies[t].financials.operating_cash_flow || 0), itemStyle: {{ color: '#22c55e' }} }},
                    {{ name: 'Capex', type: 'bar', data: tickers.map(t => companies[t].financials.capex || 0), itemStyle: {{ color: '#ef4444' }} }},
                    {{ name: 'FCF', type: 'bar', data: tickers.map(t => companies[t].financials.free_cash_flow || 0), itemStyle: {{ color: '#38bdf8' }} }}
                ]
            );

            // Debt vs Cash
            renderGroupedBarChart('chart-debt', '',
                ['Total Debt', 'Total Cash'],
                tickers,
                [
                    {{ name: 'Total Debt', type: 'bar', data: tickers.map(t => companies[t].financials.total_debt || 0), itemStyle: {{ color: '#ef4444' }} }},
                    {{ name: 'Total Cash', type: 'bar', data: tickers.map(t => companies[t].financials.total_cash || 0), itemStyle: {{ color: '#22c55e' }} }}
                ]
            );

            // Working capital
            renderGroupedBarChart('chart-wc', '',
                ['Inventory', 'Receivables'],
                tickers,
                [
                    {{ name: 'Inventory', type: 'bar', data: tickers.map(t => companies[t].financials.inventory || 0), itemStyle: {{ color: '#f59e0b' }} }},
                    {{ name: 'Receivables', type: 'bar', data: tickers.map(t => companies[t].financials.receivables || 0), itemStyle: {{ color: '#a78bfa' }} }}
                ]
            );

            // Revenue trend
            const allDates = new Set();
            tickers.forEach(t => {{
                Object.keys(companies[t].financials.revenue_trend || {{}}).forEach(d => allDates.add(d));
            }});
            const dateArr = Array.from(allDates).sort();
            renderLineChart('chart-rev-trend', '', dateArr,
                tickers.map(t => ({{
                    name: t,
                    type: 'line',
                    data: dateArr.map(d => (companies[t].financials.revenue_trend || {{}})[d] || null),
                    smooth: false,
                    showSymbol: true
                }}))
            );

            // Segment distribution
            const segData = Object.keys(segmentsData).map(seg => ({{ name: seg, value: segmentsData[seg].length }}));
            renderPieChart('chart-segment', '', segData);

            // Completeness heatmap
            const selected = screenData.candidates.filter(c => c.selected);
            const xCats = ['Income Stmt', 'Balance Sheet', 'Cashflow', 'Price Hist', 'News'];
            const yCats = selected.map(c => c.ticker);
            const heatData = [];
            selected.forEach((c, yi) => {{
                heatData.push([0, yi, c.has_income_stmt ? 1 : 0]);
                heatData.push([1, yi, c.has_balance_sheet ? 1 : 0]);
                heatData.push([2, yi, c.has_cashflow ? 1 : 0]);
                heatData.push([3, yi, c.history_rows >= 100 ? 1 : 0]);
                heatData.push([4, yi, c.news_count > 0 ? 1 : 0]);
            }});
            renderHeatmap('chart-completeness', '', xCats, yCats, heatData);

            // Valuation multiples
            renderGroupedBarChart('chart-val-multiples', '',
                ['Trailing P/E', 'Forward P/E', 'EV/EBITDA'],
                tickers,
                [
                    {{ name: 'Trailing P/E', type: 'bar', data: tickers.map(t => companies[t].market.trailing_pe == null ? 0 : companies[t].market.trailing_pe), itemStyle: {{ color: '#38bdf8' }} }},
                    {{ name: 'Forward P/E', type: 'bar', data: tickers.map(t => companies[t].market.forward_pe == null ? 0 : companies[t].market.forward_pe), itemStyle: {{ color: '#22c55e' }} }},
                    {{ name: 'EV/EBITDA', type: 'bar', data: tickers.map(t => companies[t].market.ev_ebitda == null ? 0 : companies[t].market.ev_ebitda), itemStyle: {{ color: '#f59e0b' }} }}
                ]
            );

            // Performance comparison
            const perfSeries = tickers.map(t => {{
                const rec = ohlcvData.records.find(r => r.ticker === t);
                if (!rec) return {{ name: t, type: 'line', data: [] }};
                const base = rec.bars[0].close;
                const norm = rec.bars.map(b => ((b.close - base) / base) * 100);
                return {{ name: t, type: 'line', data: norm, showSymbol: false, lineStyle: {{ width: 1.2 }} }};
            }});
            renderLineChart('chart-performance', '', ohlcvData.records[0].bars.map(b => b.date), perfSeries);

            window.addEventListener('resize', () => {{ Object.values(chartInstances).forEach(c => c && c.resize()); }});
        }}

        document.addEventListener('DOMContentLoaded', initCharts);
    </script>
</body>
</html>
"""


def note_html(note):
    return f"""
    <div class="note note-{note['type']}">
        <span class="note-ticker">{note['ticker']}</span>
        <span class="note-text">{note['text']}</span>
    </div>
    """


def valuation_row(ticker, data):
    m = data["market"]
    price = m.get("price")
    target = m.get("target_price")
    upside = None
    if price and target:
        upside = (target - price) / price
    rec_key = m.get("recommendation_key") or "N/A"
    rec_mean = m.get("recommendation_mean")
    rec_str = f"{rec_key} ({rec_mean:.2f})" if rec_mean else rec_key
    upside_str = fmt_pct(upside) if upside is not None else "N/A"
    color = "up" if (upside or 0) >= 0 else "down"
    return f"""
    <tr>
        <td><strong>{ticker}</strong></td>
        <td>{price if price is not None else 'N/A'}</td>
        <td>{target if target is not None else 'N/A'}</td>
        <td class="{color}">{upside_str}</td>
        <td>{m.get('trailing_pe') if m.get('trailing_pe') else 'N/A'}</td>
        <td>{m.get('forward_pe') if m.get('forward_pe') else 'N/A'}</td>
        <td>{m.get('ev_ebitda') if m.get('ev_ebitda') else 'N/A'}</td>
        <td>{m.get('pb_ratio') if m.get('pb_ratio') else 'N/A'}</td>
        <td>{rec_str}</td>
        <td>{fmt_pct(m.get('short_pct_float'))}</td>
    </tr>
    """


if __name__ == "__main__":
    main()
