# Clean Energy & Power Infrastructure Research Workbench Prompt

This is the prompt used in the demo. Paste it into Kimi Code (with model `k2.7`) and it will build a complete financial research dashboard for U.S. clean energy and power infrastructure stocks.

> **New to this?** Don’t worry about the length. The prompt is written for the AI, not for you. Just copy the whole thing, paste it into Kimi Code, and let it run.

## What it builds

- `research_workbench.html` — an interactive stock research dashboard in your browser
- `us_clean_energy_power_peer_comps.xlsx` — a spreadsheet comparing selected companies
- `source_inventory.xlsx` — a list of sources and data notes
- `market_ohlcv.json` — real historical stock price data
- `README.md` — notes from k2.7 about what it built

## What is OHLCV?

OHLCV stands for **Open, High, Low, Close, Volume** — the basic numbers that describe how a stock traded each day. The prompt asks k2.7 to fetch real OHLCV data before drawing any charts, so the candlestick charts are based on actual market data, not fake values.

## Theme scope

U.S.-listed clean energy and power infrastructure, including:
- Solar, storage, EV/battery exposure
- Grid infrastructure, power equipment
- Nuclear / uranium
- Independent power producers
- Utilities with data-center power demand exposure
- Data-center power / cooling infrastructure

## The prompt

```text
You are acting as a senior U.S. equity research analyst and financial data visualization designer inside an AI desktop finance product.

Task:
Build an English-language financial-terminal-style Research Workbench for a U.S.-listed clean energy and power infrastructure theme. Use available financial databases, market data tools, filings/news retrieval tools, and document-generation tools to screen companies, validate data, compare peers, create interactive charts, and deliver a local research dashboard.

Do not start with a predetermined conclusion. Let market data, filings, recent news, and company fundamentals reveal the signals.

Theme scope:
U.S.-listed clean energy and power infrastructure companies, including solar, storage, EV/battery exposure, grid infrastructure, power equipment, nuclear/uranium, independent power producers, utilities with data-center power demand exposure, and data-center power/cooling infrastructure.

Company selection:
Automatically screen a broad U.S.-listed company pool and select 8-12 key companies based on theme relevance, market attention, data availability, financial comparability, market/valuation data completeness, and verifiable business exposure.

Potential reference pool only, not required:
NEE, FSLR, ENPH, SEDG, TSLA, ALB, NXT, BE, CEG, VST, NRG, GEV, ETN, PWR, FLNC, STEM, AES, BEP, RUN.

Preserve the initial screening pool, final selections, inclusion/exclusion rationale, and missing data notes in the HTML and Excel.

Data sources:
Use available tools where relevant:
- yahoo_finance for U.S. prices, OHLCV, company info, financials, valuation metrics, analyst ratings, ownership, options/news where useful.
- stock_finance_data for cross-checking if available.
- query_stock for recent quotes, price changes, volume, technical indicators, and market snapshots.
- kimi_search_v2 / kimi_fetch_v2 for SEC filings, 10-Ks, 10-Qs, earnings releases, investor presentations, company websites, policy documents, and source verification.
- Office/document tools for Excel and HTML deliverables.

If data is unavailable, mark it as unavailable. Do not fabricate market data, financials, filings, news, or links.

Working directory:
Create:

us_clean_energy_power_research_workbench/

Save raw data, filings, source links, intermediate tables, JSON datasets, scripts, charts, and final deliverables there.

News recency:
For news, market events, policy updates, analyst commentary, and catalysts, prioritize the most recent 30 calendar days from the report generation date. Include older items only as background and label them clearly as background context. Each news item must include title, source, URL, publication date, retrieval timestamp, related ticker(s), category, and why it matters.

OHLCV / candlestick data pipeline:
Before rendering candlestick or OHLC charts, retrieve real historical OHLCV data for selected stocks and save it as:

market_ohlcv.json

For each ticker include:
- ticker
- company_name
- exchange
- currency
- data_source
- retrieval_timestamp
- date_range
- bars: date, open, high, low, close, volume

Embed the validated OHLCV JSON inside research_workbench.html as:

<script type="application/json" id="market-ohlcv-data">...</script>

Then parse it in JavaScript and render candlestick charts from that embedded JSON. Do not use screenshots, fake OHLC values, or Matplotlib images as candlestick charts. Use valid JSON values such as null, never Python values like None or nan.

HTML dashboard:
Create research_workbench.html, an English Bloomberg Terminal-style research workstation, not a normal webpage or static report.

It must include:
- Top terminal header with title, search, ticker pills, refresh control, timestamp, status, and disclaimer.
- Bloomberg-style market ticker tape / scrolling quote tape with ticker, company name, latest price, percentage change, volume or market cap.
- Left watchlist rail grouped by theme segment.
- Main tabbed workspace:
  - Market Snapshot
  - Peer Comparison
  - Candlestick / Market Charts
  - Financial Deep-Dive
  - Theme Signals
  - Evidence Feed
  - Valuation Context
- Right analyst notes panel with agreement signals, divergence signals, risk flags, watch items, and research actions.
- Bottom expandable drawer with source inventory, data limitations, audit trail, and local file paths.

Chart requirements:
All HTML charts must be interactive frontend chart components. Do not use PNG/JPG screenshots or offline Matplotlib images as chart substitutes.

Use ECharts, Plotly.js, Chart.js, or another frontend charting library. For candlestick/OHLC charts, ECharts or Plotly.js is preferred.

Charts should support hover tooltips, legends, responsive layout, click-to-expand preview modal where practical, data source labels, time range labels, and unavailable-data handling.

Include:
- Interactive candlestick / OHLC chart dashboard for at least 3-5 representative selected stocks, with volume and MA5 / MA10 / MA20 where data supports it.
- Mini sparklines for selected stocks.
- Price performance / percentage-change comparison.
- Volume or turnover comparison.
- Market cap / valuation comparison.
- Revenue or profit trend.
- Gross margin / net margin comparison.
- Cash flow, capex, inventory, or receivables risk chart where relevant.
- Theme exposure distribution or matrix.
- Evidence strength / data completeness matrix.

Evidence and links:
All important conclusions must link to evidence. HTML evidence cards and Excel source notes must include clickable URLs or local paths where possible. Avoid vague sources like “internet” or “public information”.

Deliverables:
1. research_workbench.html
2. us_clean_energy_power_peer_comps.xlsx
3. source_inventory.xlsx
4. market_ohlcv.json
5. README.md

Quality requirements:
Write like a sharp U.S. equity research analyst and design like a financial terminal product designer. Prioritize real data, traceable sources, high information density, interactive charts, clear limitations, and auditability.

Do not provide buy/sell/hold recommendations, target prices, position sizing, or trading instructions.

Before finishing, open the HTML in a browser and verify:
- All charts load.
- Candlestick/OHLC charts are visible and based on real OHLCV data.
- Console has no chart initialization errors.
- No duplicate chart container ids.
- No invalid JavaScript values such as None or nan.

End with a concise list of generated file paths.
```

## Before you run it

Make sure you have:

1. Kimi Code installed (terminal or VS Code / Cursor).
2. Logged in with `/login`.
3. Installed the **Kimi Data Source Plugin** via `/plugins` and activated it with `/kimi-datasource`.

## How to run it

1. Create or open an empty folder where you want the dashboard built.
2. Open Kimi Code:
   - Terminal: run `kimi`
   - VS Code / Cursor: open the Kimi Code panel
3. Paste the entire prompt below.
4. Wait a few minutes while k2.7 researches, builds, and verifies the dashboard.
5. Open `us_clean_energy_power_research_workbench/research_workbench.html` in your browser.
