# ⚡ Kimi Code × k2.7: Catch, Train, Ship 🐭

```
              ⚡
            /\        /\
           /  \      /  \
          /⚫  \    /  ⚫\
         /      \  /      \
        |   o      o      |
        |  (O)      (O)   |
        |       v         |
         \    ⌒  ⌒       /
          \_____________/
```

> *“To become a Pokémon Master of Code, you must first choose your starter.”*

Welcome, trainer! 🌟

This repo is an **open-source showcase** of how to go from a fresh install of **[Kimi Code](https://www.kimi.com/code)** to a fully shipped, interactive financial research terminal — powered by Moonshot’s latest model, **k2.7**.

No slide decks. No fake mockups. Just one detailed prompt, real market data, and a real Bloomberg-style dashboard running locally in your browser.

---

## 🎥 What this repo demonstrates

The journey is simple:

1. **Catch Kimi Code** — install it in your terminal.
2. **Train it in your IDE** — add the Kimi Code extension to VS Code or Cursor.
3. **Log in once** with `/login`.
4. **Issue one big prompt** and watch k2.7 evolve your idea into a real product.
5. **Open the generated HTML dashboard** and explore real charts, tickers, and filings.

One idea → one prompt → one shipped research terminal.

---

## 🥚 Choose Your Starter

Before you can challenge the Pokémon League, you need a partner. Pick yours:

| Starter | Path | Best for | Difficulty |
|---------|------|----------|------------|
| 🔥 **Charmander** | Terminal | Trainers who live in the command line | Easy |
| 💧 **Squirtle** | VS Code / Cursor | Trainers who like panels and buttons | Easy |

You only need one starter. Both evolve into the same champion.

---

## 🔥 Charmander Route: Terminal

### Step 1: Catch your Kimi

Throw your install ball:

**macOS / Linux:**

```bash
curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash
```

**Windows (PowerShell):**

```powershell
Invoke-RestMethod https://code.kimi.com/kimi-code/install.ps1 | Invoke-Expression
```

### Step 2: Wake up your shell

If `kimi` isn’t found, reload your shell:

```bash
source ~/.zshrc   # or ~/.bashrc
```

Or open a fresh terminal tab — like starting a new route.

### Step 3: Log in at the Pokémon Center

```bash
kimi
```

Then type:

```
/login
```

A browser window opens. That’s your trainer card verification. 🪪

### Step 4: Start battling

```bash
kimi
```

Then issue your first command:

```
Build me a React app that looks like a Pokédex
```

---

## 💧 Squirtle Route: VS Code / Cursor

Prefer a partner swimming alongside you in the IDE?

1. Open **Extensions** (`Cmd+Shift+X` / `Ctrl+Shift+X`).
2. Search **“Kimi Code”** and install it. ✨
3. Open the Kimi Code panel from the sidebar.
4. Run `/login` in the extension terminal.
5. Start coding — *“I choose you, Kimi!”*

> 💡 *Cursor is built on VS Code, so the same extension usually works. If it’s not in Cursor’s marketplace, the Charmander route is just as powerful.*

---

## 🧰 Teaching Kimi New Moves: Plugins

Kimi Code can learn extra moves through plugins. For the research terminal demo, you’ll want the **Kimi Data Source Plugin** so Kimi can pull real market data, filings, and news.

### Install the plugin

Inside Kimi Code (terminal or IDE panel), type:

```
/plugins
```

Find and install **Kimi Data Source Plugin**.

### Use it

Once installed, activate it with:

```
/kimi-datasource
```

Now Kimi can call financial data tools like `yahoo_finance`, `query_stock`, `kimi_search_v2`, and `kimi_fetch_v2` — the same ones the big prompt below will use.

Think of it as teaching your partner Surf before crossing the ocean. 🌊

---

## 🚀 The Main Event: Build the Research Terminal

Once Kimi Code is set up and the data plugin is installed, you can recreate the showcase demo in minutes.

### Step 1: Send out Kimi

Open it in the terminal:

```bash
kimi
```

Or open the Kimi Code panel in VS Code / Cursor.

### Step 2: Use the ultimate move

Copy the full prompt from **[`prompt.md`](./prompt.md)**.

It tells k2.7 to build a **financial-terminal-style Research Workbench** for U.S. clean energy and power infrastructure stocks, including:

- Real OHLCV market data
- SEC filings and recent news
- Interactive candlestick charts
- Peer comparison tables
- A Bloomberg-style HTML dashboard
- Excel workbooks for sources and peer comps

### Step 3: Let it evolve

k2.7 will:

1. Screen 8–12 relevant stocks.
2. Pull market data, filings, and news.
3. Build `research_workbench.html` and supporting Excel/JSON files.
4. Open the HTML in a browser to verify the charts load correctly.

### Step 4: Explore your gym badge

Open this file in your browser:

```
us_clean_energy_power_research_workbench/research_workbench.html
```

You should see a scrolling ticker tape, watchlists, tabbed workspaces, and interactive charts — all backed by real data.

---

## 🧭 Kimi Pokédex

| Command | Effect |
|---------|--------|
| `kimi --version` | Check your partner’s level |
| `kimi --thinking` | Use a powered-up attack (deeper reasoning) |
| `/login` | Verify your trainer card |
| `/setup` | Configure your API key manually |
| `/sessions` | View your saved adventures |
| `kimi --continue` | Resume your last quest |

---

## 🏆 Elite Four Tips

- Use `@filename` to point Kimi at a specific file, like commanding a Pokémon to attack.
- Press `Ctrl-X` in the CLI to switch to shell mode — great for quick items.
- Run `/compact` when your context bar gets high, like healing at a Pokémon Center.
- The prompt in [`prompt.md`](./prompt.md) is long on purpose: k2.7 handles the complexity so you don’t have to.

---

## 📦 What gets generated

After running the prompt, you’ll find a new folder:

```
us_clean_energy_power_research_workbench/
├── research_workbench.html          # Interactive financial terminal
├── us_clean_energy_power_peer_comps.xlsx
├── source_inventory.xlsx
├── market_ohlcv.json                # Real historical OHLCV data
└── README.md                        # Notes from k2.7 about the build
```

---

## 📜 Professor’s References

- [Kimi Code official site](https://www.kimi.com/code)
- [Kimi Code CLI on GitHub](https://github.com/MoonshotAI/kimi-cli)
- [Kimi Code introduction](https://www.kimi.com/resources/kimi-code-introduction)

---

## 🤝 Open Source

This repo is meant to be an open Pokédex. Fork it, remix the prompt, swap the theme, or use it as a starting point for your own k2.7 demos.

If you build something cool, share it. The Pokémon League has room for many champions. ⚡

---

*May your builds pass and your bugs be few.*

*“I’m gonna be a Pokémon Master… of Code!”* 👑
