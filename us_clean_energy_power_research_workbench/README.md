# U.S. Clean Energy & Power Infrastructure — Research Workbench

An English-language, Bloomberg Terminal-style research dashboard for a U.S.-listed clean-energy and power-infrastructure theme. Built from market data, fundamentals, news, and an automated screening pipeline.

**Report generated:** 2026-06-13  
**Data source:** Yahoo Finance via `yfinance` (Python)

---

## Deliverables

| File | Description |
|------|-------------|
| `research_workbench.html` | Interactive terminal-style dashboard with embedded real OHLCV data and ECharts visualizations |
| `us_clean_energy_power_peer_comps.xlsx` | Peer comparison, revenue trend, screening/selection rationale, and news feed |
| `source_inventory.xlsx` | Source inventory, audit trail, and data-limitation notes |
| `market_ohlcv.json` | Real 1-year daily OHLCV bars for the selected universe |
| `README.md` | This file |
| `raw/candidate_screen.json` | Full screening pool, scores, and selection rationale |
| `raw/final_company_data.json` | Market data, fundamentals, and business summaries for selections |
| `raw/news_feed.json` | Recent and background news items with URLs and metadata |

---

## Selected Universe (10 companies)

| Ticker | Company | Theme Segment |
|--------|---------|---------------|
| ENPH | Enphase Energy, Inc. | Solar / Inverters / Tracking |
| NXT | Nextpower Inc. | Solar / Inverters / Tracking |
| TSLA | Tesla, Inc. | Batteries / EV / Materials |
| GEV | GE Vernova Inc. | Grid / Power Equipment |
| PWR | Quanta Services, Inc. | Grid / Power Equipment |
| NEE | NextEra Energy, Inc. | Nuclear / IPP / Utility / Data-Center Power |
| VST | Vistra Corp. | Nuclear / IPP / Utility / Data-Center Power |
| NRG | NRG Energy, Inc. | Nuclear / IPP / Utility / Data-Center Power |
| AES | The AES Corporation | Nuclear / IPP / Utility / Data-Center Power |
| CEG | Constellation Energy Corporation | Nuclear / IPP / Utility / Data-Center Power |

---

## Reference Pool

The initial screening pool contained 19 tickers:

`NEE, FSLR, ENPH, SEDG, TSLA, ALB, NXT, BE, CEG, VST, NRG, GEV, ETN, PWR, FLNC, STEM, AES, BEP, RUN`

Selections were made by a composite score blending theme relevance, data completeness, market-cap liquidity, and analyst coverage. At least one representative from each theme segment was guaranteed before filling remaining slots by composite rank.

Notable exclusions include FSLR, ALB, SEDG, ETN, BE, FLNC, STEM, BEP, and RUN, which were eligible but ranked below the top composite/segment slots. Rationale is preserved in the HTML and Excel screening sheets.

---

## Dashboard Features

- **Terminal header** with search, ticker pills, live timestamp, status, and disclaimer
- **Scrolling quote tape** with price, change, and volume
- **Left watchlist rail** grouped by theme segment
- **Tabbed workspace:**
  - Market Snapshot
  - Peer Comparison
  - Candlestick / OHLC Charts
  - Financial Deep-Dive
  - Theme Signals
  - Evidence Feed
  - Valuation Context
- **Right analyst notes panel** with agreement, divergence, risk flags, watch items, and research actions
- **Bottom drawer** with source inventory, data limitations, audit trail, and local file paths
- **Interactive ECharts** for candlesticks, performance, valuation, margins, cash flow, debt, working capital, revenue trends, theme exposure, and data completeness

---

## Data Notes & Limitations

- Prices and OHLCV are sourced from Yahoo Finance and are adjusted for splits and dividends where applicable.
- Financial statement extracts use the most recent annual reports available; quarterly items approximate TTM.
- Missing values are stored as JSON `null` / Excel blanks. No values are fabricated.
- News coverage depends on Yahoo Finance aggregation; paywalled sources may be omitted.
- Timestamps are in UTC.

---

## Usage

Open `research_workbench.html` in any modern browser with internet access (ECharts loads from CDN). All market data is embedded, so the file works locally without a server.

---

## GitHub Deployment & Automation

### 1. Host the dashboard on GitHub Pages

The workbench is a self-contained static HTML file. You can publish it directly from any GitHub repository branch:

1. Push this directory to a GitHub repository:
   ```bash
   cd us_clean_energy_power_research_workbench
   git init
   git add .
   git commit -m "Initial clean energy research workbench"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

2. Enable GitHub Pages:
   - Go to **Settings → Pages** in the repository.
   - Under **Build and deployment → Source**, select **Deploy from a branch**.
   - Choose the `main` branch and the `/ (root)` folder.
   - Click **Save**.

3. After the workflow runs (usually within 1–2 minutes), your dashboard will be live at:
   ```
   https://<your-username>.github.io/<your-repo>/research_workbench.html
   ```

   Because all market data is embedded in `research_workbench.html`, the published page requires no backend.

### 2. Refresh data with GitHub Actions

A sample workflow (`.github/workflows/refresh-workbench.yml`) is included. It:

- Runs on a schedule (e.g., weekly) or on manual trigger.
- Sets up Python and installs dependencies.
- Re-runs the fetch/build pipeline.
- Commits updated data, HTML, and Excel files back to the repository.

To use it:

1. Ensure the workflow file is present at `.github/workflows/refresh-workbench.yml`.
2. In GitHub, go to **Actions → Workflows → Refresh Research Workbench** and click **Run workflow**.
3. Optionally edit the `cron` line in the workflow to change the refresh cadence.

### 3. Run locally (no GitHub required)

```bash
cd us_clean_energy_power_research_workbench
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Fetch fresh data
python3 1_fetch_data.py

# Rebuild Excel files
python3 2_build_excel.py

# Rebuild HTML dashboard
python3 3_build_html.py

# Open dashboard
open research_workbench.html
```

> **Note:** Running `1_fetch_data.py` calls Yahoo Finance and may take a few minutes. Respect Yahoo's terms of service and avoid excessive refresh frequency.

---

## Important Disclaimer

This workbench is for research and visualization purposes only. It does **not** provide buy/sell/hold recommendations, target prices, position sizing, or trading instructions.
