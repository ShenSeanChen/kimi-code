# ⚡ Kimi Code × k2.7: From Setup to Shipped Terminal 🏴‍☠️

> *“To become the King of Code, you must first choose your path.”*

Welcome, trainer — or should I say, pirate captain! 🌊

This repo is an **open-source showcase** of how to go from a fresh install of **[Kimi Code](https://www.kimi.com/code)** to a fully shipped, interactive financial research terminal — powered by Moonshot’s latest model, **k2.7**.

No slide decks. No fake mockups. Just a real prompt, real market data, and a real Bloomberg-style dashboard that you can run locally in your browser.

---

## 🎥 What this repo demonstrates

The journey looks like this:

1. **Install Kimi Code** in your terminal.
2. **Install the Kimi Code extension** in VS Code or Cursor.
3. **Log in once** with `/login`.
4. **Paste one detailed prompt** and let k2.7 do the rest.
5. **Open the generated HTML dashboard** and explore real charts, tickers, and filings.

That’s it. One idea → one prompt → one shipped research terminal.

---

## 🥚 Choose Your Starter

Before you can sail the Grand Line, you need a companion. Pick your path:

| Path | Best for | Difficulty |
|------|----------|------------|
| 🗡️ **Terminal** | Pirates who live in the command line | Easy |
| 🧩 **VS Code / Cursor** | Trainers who like buttons and sidebars | Easy |

You only need one. Both connect to the same agent.

---

## 🗡️ Path 1: Terminal (The Zoro Route)

### 1. Catch your Kimi

**macOS / Linux:**

```bash
curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash
```

**Windows (PowerShell):**

```powershell
Invoke-RestMethod https://code.kimi.com/kimi-code/install.ps1 | Invoke-Expression
```

### 2. Wake up your shell

If `kimi` isn’t found, reload your shell:

```bash
source ~/.zshrc   # or ~/.bashrc
```

Or open a new terminal tab like discovering a new island on the Grand Line.

### 3. Log in

```bash
kimi
```

Then type:

```
/login
```

A browser window will open. That’s your Pokédex… I mean, authentication flow. 📱

### 4. You’re ready

```bash
kimi
```

Now challenge it with anything:

```
Build me a React app that looks like a Pokédex
```

---

## 🧩 Path 2: VS Code / Cursor (The Ash Route)

Prefer a partner by your side? Here’s the IDE path:

1. Open **Extensions** (`Cmd+Shift+X` / `Ctrl+Shift+X`).
2. Search **“Kimi Code”** and install it. ✨
3. Open the Kimi Code panel from the sidebar.
4. Run `/login` in the extension terminal.
5. Start coding — *“I choose you, Kimi!”*

> 💡 *Cursor is built on VS Code, so the same extension usually works. If Cursor’s marketplace doesn’t have it, the Terminal path above is just as strong.*

---

## 🚀 The Main Event: Build the Research Terminal

Once Kimi Code is set up, you can recreate the showcase demo in minutes.

### Step 1: Open Kimi Code

Use the terminal:

```bash
kimi
```

Or open the Kimi Code panel in VS Code / Cursor.

### Step 2: Paste the prompt

Copy the full prompt from **[`prompt.md`](./prompt.md)**.

It asks k2.7 to build a **financial-terminal-style Research Workbench** for U.S. clean energy and power infrastructure stocks, complete with:

- Real OHLCV market data
- SEC filings and recent news
- Interactive candlestick charts
- Peer comparison tables
- A Bloomberg-style HTML dashboard
- Excel workbooks for sources and peer comps

### Step 3: Let it cook

k2.7 will:

1. Screen 8–12 relevant stocks.
2. Pull market data, filings, and news.
3. Build `research_workbench.html` and the supporting Excel/JSON files.
4. Open the HTML in a browser to verify the charts load correctly.

### Step 4: Explore your terminal

Open this file in your browser:

```
us_clean_energy_power_research_workbench/research_workbench.html
```

You should see a scrolling ticker tape, watchlists, tabbed workspaces, and interactive charts — all backed by real data.

---

## 🧭 Command Pokédex

Handy commands once you’re sailing:

| Command | Effect |
|---------|--------|
| `kimi --version` | Check your companion’s level |
| `kimi --thinking` | Use deeper reasoning (like entering Gear 2) |
| `/login` | Log in via browser |
| `/setup` | Configure API key manually |
| `/sessions` | View your saved adventures |
| `kimi --continue` | Resume your last quest |

---

## 🏆 Final Boss Tips

- Use `@filename` to point Kimi at a specific file, like calling a Pokémon to the field.
- Press `Ctrl-X` in the CLI to drop into shell mode — great for quick commands.
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

## 📜 Scrolls of Wisdom

- [Kimi Code official site](https://www.kimi.com/code)
- [Kimi Code CLI on GitHub](https://github.com/MoonshotAI/kimi-cli)
- [Kimi Code introduction](https://www.kimi.com/resources/kimi-code-introduction)

---

## 🤝 Open Source

This repo is meant to be an open terminal. Fork it, remix the prompt, swap the theme, or use it as a starting point for your own k2.7 demos.

If you build something cool, share it. The Grand Line is long, and there’s room for many crews. 🌟

---

*May your builds pass and your bugs be few.*

*“I’m gonna be King of the Coders!”* 👑
